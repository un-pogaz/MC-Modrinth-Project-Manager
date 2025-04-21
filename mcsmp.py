import argparse
from sys import argv
import os
import json
from collections import namedtuple
from datetime import datetime

import requests
requests = requests.Session()
requests.headers.update({'User-Agent':'un-pogaz/MC-Modrinth-Project-Manager (un.pogaz@gmail.com)'})

def join(*args: str):
    return os.path.join(*args).replace('\\', '/')

def _json(path, data=None):
    if data is not None:
        with open(path, 'wt', newline='\n', encoding='utf-8') as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    
    else:
        if not os.path.exists(path):
            return {}
        
        with open(path, 'rb') as f:
            return json.loads(f.read())

def sort_dict(dic):
    return {kv[0]:kv[1] for kv in sorted(dic.items(), key=lambda item: item[0].casefold())}

def root(data=None):
    if data:
        data = sort_dict(data)
    return sort_dict(_json('mcsmp.json', data))

def mcsmp_path(path):
    return join(path, '.mcsmp.json')

class MCSMP(dict):
    def __init__(self, directory: str, exit_if_error=True):
        self._directory = directory
        self._path = None
        self._mcsmp_path = None
        self._load_data(exit_if_error=exit_if_error)
    
    def _load_data(self, *, exit_if_error=True):
        self._path = root().get(self.directory, None)
        
        if not self.path:
            print(f'The directory {self.directory!r} his not defined')
            return exit() if exit_if_error else None
        
        if not os.path.exists(self.path):
            print(f"The path {self._path!r} of the directory {self.directory!r} doesn't exist")
            return exit() if exit_if_error else None
        
        edited = False
        self._mcsmp_path = mcsmp_path(self.path)
        if not os.path.exists(self.mcsmp_path):
            edited = True
        else:
            self.update(_json(self.mcsmp_path))
        
        for k in ['game_version', 'loader', 'loader_shader']:
            if k not in self:
                self[k] = None
                edited = True
        for k in list(project_types.keys()) + list(project_types_world.keys()):
            if k not in self:
                self[k] = {}
                edited = True
            
            self[k] = sort_dict(self[k])
        
        for k in project_types_world.keys():
            for kk in list(self[k].keys()):
                w = self[k][kk]
                if w:
                    self[k][kk] = sort_dict(w)
                else:
                    del self[k][kk]
                    edited = True
        
        if edited:
            self.commit()
    
    @property
    def directory(self) -> str:
        return self._directory
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def mcsmp_path(self) -> str:
        return self._mcsmp_path
    
    @property
    def version(self) -> str:
        return self['game_version']
    @version.setter
    def version(self, value):
        self['game_version'] = value
    
    @property
    def loader(self) -> str:
        return self['loader']
    @loader.setter
    def loader(self, value):
        self['loader'] = value
    
    @property
    def loader_shader(self) -> str:
        return self['loader_shader']
    @loader_shader.setter
    def loader_shader(self, value):
        self['loader_shader'] = value
    
    
    @property
    def mod(self) -> dict[str, str]:
        return self['mod']
    @mod.setter
    def mod(self, value):
        self['mod'] = value
    
    @property
    def resourcepack(self) -> dict[str, str]:
        return self['resourcepack']
    @resourcepack.setter
    def resourcepack(self, value):
        self['resourcepack'] = value
    
    @property
    def datapack(self) -> dict[str, dict[str, str]] :
        return self['datapack']
    @datapack.setter
    def datapack(self, value):
        self['datapack'] = value
    
    @property
    def shader(self) -> dict[str, str]:
        return self['shader']
    @shader.setter
    def shader(self, value):
        self['shader'] = value
    
    def commit(self):
        _json(self.mcsmp_path, self)

def safe_del(path):
    from shutil import rmtree
    
    def remove(a):
        pass
    
    if os.path.exists(path):
        if os.path.isfile(path):
            remove = os.remove
        if os.path.isdir(path):
            remove = rmtree
        if os.path.islink(path):
            remove = os.unlink
    
    try:
        remove(path)
    except Exception:
        pass

class Cache:
    _cachefolder = join(os.path.dirname(argv[0]), '.cache')
    def _make_cachefolder():
        cache_version = join(Cache._cachefolder, '.v1')
        if not os.path.exists(cache_version):
            Cache.clear_cache()
        
        if not os.path.exists(Cache._cachefolder):
            os.makedirs(Cache._cachefolder, exist_ok=True)
            with open(cache_version, 'wt', newline='\n', encoding='utf-8') as f:
                f.write('')
    
    def clear_cache(files=None):
        if files:
            for f in files:
                safe_del(join(Cache._cachefolder, f))
            
            print('Cache files cleaned: ' + ', '.join(files))
        else:
            safe_del(Cache._cachefolder)
            if files is not None:
                print('Cache folder cleaned')
    
    
    _project = None
    _project_path = join(_cachefolder, 'project')
    
    def _read_project():
        if not Cache._project:
            Cache._project = _json(Cache._project_path)
    
    def add_project(id, slug):
        Cache._read_project()
        if id not in Cache._project:
            Cache._project[id] = slug
            Cache._make_cachefolder()
            _json(Cache._project_path, Cache._project)
    
    def get_project(id):
        Cache._read_project()
        return Cache._project.get(id, None)
    
    
    _version = None
    _version_path = join(_cachefolder, 'version')
    
    def _read_version():
        if not Cache._version:
            Cache._version = _json(Cache._version_path)
    
    def add_version(id, slug):
        Cache._read_version()
        if id not in Cache._version:
            Cache._version[id] = slug
            Cache._make_cachefolder()
            _json(Cache._version_path, Cache._version)
    
    def get_version(id):
        Cache._read_version()
        return Cache._version.get(id, None)
    
    
    _slug = None
    _slug_path = join(_cachefolder, 'slug')
    
    def _read_slug():
        if not Cache._slug:
            Cache._slug = _json(Cache._slug_path)
    
    def add_slug(slug, id, type):
        Cache._read_slug()
        if slug not in Cache._slug:
            Cache._slug[slug] = {'id':id,'project_type':type}
            Cache._make_cachefolder()
            _json(Cache._slug_path, Cache._slug)
    
    def get_slug(slug):
        Cache._read_slug()
        return Cache._slug.get(slug, None)

HASH_ALGO = 'sha1'
def hash_file(file):
    if os.path.exists(file):
        import hashlib
        with open(file, 'rb') as f:
            hash = hashlib.file_digest(f, HASH_ALGO)
        return hash.hexdigest()
    return None


def directory_add(directory, path):
    path = os.path.abspath(path).replace('\\', '/')
    if not os.path.exists(path):
        print(f"The path {path!r} doesn't exist")
        exit()
    
    if not os.path.isdir(path):
        print(f'The path {path!r} is not a folder')
        exit()
    
    r = root()
    for k,v in r.items():
        if path == v and directory != k:
            print(f'The path {path!r} is already assosiated to the directory {k!r}')
            exit()
    
    path_old = r.get(directory, None)
    r[directory] = path
    root(r)
    
    if path_old and path_old != path:
        if not os.path.exists(path):
            _json(mcsmp_path(path), _json(mcsmp_path(path_old)))
        safe_del(mcsmp_path(path_old))
    
    data = MCSMP(directory)
    
    print(f'Directorie {directory!r} added')
    if not data.version and not data.loader:
        print(f"Don't forget to set a {data.version!r} for Minecraft and a {data.loader!r}")
    elif not data.version:
        print(f"Don't forget to set a {data.version!r} for Minecraft")
    elif not data.loader:
        print(f"Don't forget to set a {data.loader!r}")

def directory_remove(directory):
    r = root()
    if directory in r:
        del r[directory]
        root(r)
        print(f"The directory {directory} has been removed")
    else:
        print(f"No directory {directory} defined to remove")


def directory_version(directory, version=None):
    data = MCSMP(directory)
    if version:
        data.version = version
        data.commit()
    print(f'Directorie {directory!r} is set to the version: {data.version}')

def directory_loader(directory, loader=None):
    data = MCSMP(directory)
    if loader:
        data.loader = loader.lower()
        data.commit()
    print(f'Directorie {directory!r} is set to the loader: {data.loader}')

def directory_shader(directory, loader=None):
    data = MCSMP(directory)
    if loader:
        data.loader_shader = loader.lower() or None
        data.commit()
    print(f'Directorie {directory!r} is set to the shader loader: {data.loader_shader}')


def test_version(directory, data: MCSMP, _exit=True):
    if not data.version:
        print(f'The directory {directory!r} has no defined version')
        if _exit:
            exit()
        else:
            return False
    return True

def test_loader(directory, data: MCSMP, _exit=True):
    test_version(directory, data)
    if not data.loader:
        print(f'The directory "{directory!r} has no defined loader')
        if _exit:
            exit()
        else:
            return False
    return True

def test_shader(directory, data: MCSMP, _exit=True):
    test_version(directory, data)
    if not data.loader:
        print(f'The directory "{directory!r} has no defined loader')
        if _exit:
            exit()
        else:
            return False
    return True

def test_world(directory, data: MCSMP, world, _exit=True):
    test_version(directory, data)
    if not os.path.exists(join(data.path, 'saves', world)):
        print(f'The directory {directory!r} has no world named {world!r}')
        if _exit:
            exit()
        else:
            return False
    return True


ProjectType = namedtuple('ProjectType', 'folder test')
project_types = {
    'resourcepack': ProjectType('resourcepacks', test_version),
    'mod': ProjectType('mods', test_loader),
    'shader': ProjectType('shaderpacks', test_shader),
}
project_types_world = {
    'datapack': ProjectType('datapacks', test_world),
}
loaders_alt = {'quilt': ['fabric']}
loaders_mods_swap = {'quilt': {'fabric-api':'qsl'}}

def test_filename(path_filename):
    enabled = True
    if not os.path.exists(path_filename) and os.path.exists(path_disabled(path_filename)):
        enabled = False
    present = True
    if not os.path.exists(path_filename) and not os.path.exists(path_disabled(path_filename)):
        present = False
        enabled = False
    
    return enabled, present
def get_print_filename(enabled, present):
    return ('' if enabled else (' [disabled]' if present else ' !!not present!!'))


def list_directorys():
    r = root()
    if not r:
        print('No directorys has defined')
        return
    for name in r:
        data = MCSMP(name, exit_if_error=False)
        if data:
            print(f'"{name}" : {data.version}/{data.loader} => "{data.path}"')

def list_projects(directory):
    data = MCSMP(directory, exit_if_error=False)
    if not data:
        return
    
    print(f'"{directory}" : {data.version}/{data.loader} => "{data.path}"')
    
    for type, pt in project_types.items():
        if data[type] and pt.test(directory, data, False):
            print()
            print(f'--== Installed {pt.folder} ==--')
            for urlslug in data[type]:
                enabled, present = test_filename(join(data.path, pt.folder, data[type][urlslug]))
                print(urlslug + get_print_filename(enabled, present))

def list_world_projects(directory, world):
    data = MCSMP(directory, exit_if_error=False)
    if not data:
        return
    
    print(f'"{directory}" : {data.version}/{data.loader} => "{data.path}"')
    
    test_world(directory, data, world)
    for type, pt in project_types_world.items():
        if pt.test(directory, data, world, False):
            if world in data[type] and data[type][world]:
                world_path = join(data.path, 'saves', world, pt.folder)
                print()
                print(f'--== Installed {pt.folder} in the world "{world}" ==--')
                for urlslug in data[type][world]:
                    enabled, present = test_filename(join(world_path, data[type][world][urlslug]))
                    print(urlslug + get_print_filename(enabled, present))


def project_check(directory, urlslug, world=None):
    urlslug = urlslug.lower()
    data = MCSMP(directory)
    test_version(directory, data)
    
    if world:
        test_world(directory, data, world)
        for type, pt in project_types_world.items():
            if world in data[type]:
                world_path = join(data.path, 'saves', world, pt.folder)
                if urlslug in data[type][world]:
                    enabled, present = test_filename(join(world_path, data[type][world][urlslug]))
                    print(f'{urlslug!r} is installed in the world {world!r} of the directory {directory!r}'+ get_print_filename(enabled, present))
                    if not present:
                        print('but the file are not present! Reinstal the project')
                    return
                
        print(f'{urlslug!r} is not installed in the world {world!r} of the directory {directory!r}')
    
    else:
        for type, pt in project_types.items():
            if urlslug in data[type]:
                enabled, present = test_filename(join(data.path, pt.folder, data[type][urlslug]))
                print(f'{urlslug!r} is installed in the directory {directory!r}'+ get_print_filename(enabled, present))
                if not present:
                    print('but the file are not present! Reinstal the project')
                return
    
        print(f'{urlslug!r} is not installed in the directory {directory!r}')


def path_disabled(path):
    return path+'.disabled'
def path_enable(data, type, urlslug, enable, world=None):
    urlslug = urlslug.lower()
    if world:
        path_filename = join(data.path, 'saves', world, project_types_world[type].folder, data[type][world][urlslug])
    else:
        path_filename = join(data.path, project_types[type].folder, data[type][urlslug])
    
    if enable and os.path.exists(path_disabled(path_filename)):
        os.rename(path_disabled(path_filename), path_filename)
    
    if not enable and os.path.exists(path_filename):
        os.rename(path_filename, path_disabled(path_filename))


def link(*wanted):
    return 'https://api.modrinth.com/v2/' + '/'.join(wanted)

def project_install(directory, urlslug, world=None):
    data = MCSMP(directory)
    if install_project_file(directory, data, urlslug, world):
        data.commit()

def project_update(directory, world=None):
    data = MCSMP(directory)
    
    total = []
    errors = []
    
    if world:
        for type, pt in project_types_world.items():
            if pt.test(directory, data, world, False):
                if world in list(data[type].keys()):
                    for urlslug in data[type][world]:
                        rslt = install_project_file(directory, data, urlslug, world)
                        if rslt is None:
                            errors.append(urlslug)
                        if rslt:
                            total.append(urlslug)
                            data.commit()
                        print()
        
        print(f'Finaly! {len(total)} projects has been updated in the world {world!r}" of {directory!r}')
    
    else:
        for type, pt in project_types.items():
            if pt.test(directory, data, False):
                for urlslug in list(data[type].keys()):
                    rslt = install_project_file(directory, data, urlslug)
                    if rslt is None:
                        errors.append(urlslug)
                    if rslt:
                        total.append(urlslug)
                        data.commit()
                    print()
        
        print(f'Finaly! {len(total)} projects has been updated in {directory!r}')
    
    if total:
        print('Updated projects: ' + ', '.join(total))
    if errors:
        print('but... the following projects have suffered an error during their download:')
        print(', '.join(errors))

def install_project_file(directory, data: MCSMP, urlslug, world=None):
    urlslug = urlslug.lower()
    loader = data.loader
    
    project_data = Cache.get_slug(urlslug)
    if not project_data:
        urllink = link('project', urlslug)
        url = requests.get(urllink)
        if not url.ok:
            print(f"Error during url request, the project {urlslug} probably doesn't exist")
            return None
        
        project_data = json.loads(url.content)
    
    project_id = project_data['id']
    project_type = project_data['project_type']
    Cache.add_project(project_id, urlslug)
    Cache.add_slug(urlslug, project_id, project_type)
    
    
    if world:
        if project_type == 'mod':
            project_type = 'datapack'
        
        if project_type not in project_types_world:
            print(f"The project {urlslug} has a type {project_type!r} incompatible with the argument [World]")
            return False
        
        pt = project_types_world[project_type]
        pt.test(directory, data, world)
        base_path = join(data.path, 'saves', world, pt.folder)
    else:
        
        if project_type not in project_types:
            print(f"The project {urlslug} has a type {project_type!r} incompatible for a global install")
            return False
        
        pt = project_types[project_type]
        pt.test(directory, data)
        base_path = join(data.path, pt.folder)
    
    if project_type == 'resourcepack':
        loader = 'minecraft'
    if project_type == 'shader':
        loader = data.loader_shader
    if project_type == 'datapack':
        loader = 'datapack'
    
    print(f"Fetching versions of {urlslug} for Minecraft {data.version!r} and the loader {loader!r}...")
    
    if loader:
        all_loaders = [loader]+loaders_alt.get(loader, [])
    else:
        all_loaders = []
    
    params = {
        'game_versions': f'["{data.version}"]',
        'loaders': '['+','.join(['"'+x+'"' for x in all_loaders])+']'
    }
    versions = json.loads(requests.get(link('project', project_id, 'version'), params=params).content)
    
    valide_versions = []
    if all_loaders:
        for _loader in all_loaders:
            for v in versions:
                if _loader in v['loaders']:
                    valide_versions.append(v)
                    break
            if len(valide_versions) == len(all_loaders):
                break
    elif versions:
        valide_versions.append(versions[0])
    
    version_project = None
    for v in valide_versions:
        if not version_project:
            version_project = v
        if datetime.fromisoformat(version_project['date_published']) < datetime.fromisoformat(v['date_published']):
            version_project = v
    
    if not version_project:
        print("No version available")
    
    else:
        Cache.add_version(version_project['id'], urlslug)
        version_file = version_project['files'][0]
        
        if project_type == 'shader' and version_project['loaders'][0] in ['vanilla', 'canvas']:
            base_path = join(data.path, 'resourcepacks')
        
        os.makedirs(base_path, exist_ok=True)
        
        filename = version_file['filename']
        if world:
            filename_old = data[project_type].get(world, {}).get(urlslug, None)
        else:
            filename_old = data[project_type].get(urlslug, None)
        path_filename = join(base_path, filename)
        
        print(f"Got the link for {filename!r}")
        
        disabled = False
        if os.path.exists(path_disabled(path_filename)):
            disabled = True
            os.rename(path_disabled(path_filename), path_filename)
        
        if filename_old:
            path_filename_old = join(base_path, filename_old)
            if os.path.exists(path_disabled(path_filename_old)):
                disabled = True
                os.rename(path_disabled(path_filename_old), path_filename_old)
        
        installed = False
        if filename_old and filename_old == filename and hash_file(path_filename) == version_file['hashes'][HASH_ALGO]:
            if world:
                print(f'The project {urlslug!r} is already up to date in the world {world!r} of {directory!r}')
            else:
                print(f'The project {urlslug!r} is already up to date in {directory!r}')
        
        else:
            print("Downloading project...")
            url = requests.get(version_file['url'])
            if url.ok:
                with open(path_filename, 'wb') as f:
                    f.write(url.content)
            else:
                print("Downloading fail!")
                return None
            
            if filename_old and filename_old != filename:
                safe_del(path_filename_old)
            
            if world:
                if world not in data[project_type]:
                    data[project_type][world] = {}
                data[project_type][world][urlslug] = filename
                
                print(f'Done! The project {urlslug!r} has been installed in the world {world!r} of {directory!r}')
            else:
                data[project_type][urlslug] = filename
                print(f'Done! The project {urlslug!r} has been installed in {directory!r}')
            installed = True
        
        if world:
            if len(version_project['files']) >= 2:
                assets_file = version_project['files'][1]
                assets_path = join(data.path, 'resourcepacks', assets_file['filename'])
                if hash_file(assets_path) != assets_file['hashes'][HASH_ALGO]:
                    print("Downloading additional assets...")
                    url = requests.get(assets_file['url'])
                    if url.ok:
                        with open(assets_path, 'wb') as f:
                            f.write(url.content)
                    else:
                        print("Downloading additional assets fail!")
        
        if disabled:
            os.rename(path_filename, path_disabled(path_filename))
        
        def get_id_slug(dependencie):
            try:
                v_slug = None
                p_slug = None
                versionid = dependencie['version_id']
                
                if versionid:
                    v_slug = Cache.get_version(versionid)
                    if not v_slug:
                        projectid = json.loads(requests.get(link('version', versionid)).content)['project_id']
                    else:
                        projectid = None
                else:
                    projectid = dependencie['project_id']
                
                if projectid:
                    p_slug = Cache.get_project(projectid)
                
                if not p_slug and projectid:
                    full_project = json.loads(requests.get(link('project', projectid)).content)
                    p_slug = full_project['slug']
                    Cache.add_project(projectid, p_slug)
                
                if not v_slug and versionid and p_slug:
                    Cache.add_version(versionid, p_slug)
                
                return p_slug or v_slug
            except Exception:
                return None
        
        def is_installed(dependencie):
            for type in project_types:
                if dependencie in data[type]:
                    return True
            
            return False
        
        dependencies = [get_id_slug(d) for d in version_project['dependencies'] if d['dependency_type'] in ['required', 'embedded']]
        dependencies = {d for d in dependencies if d}
        for kv in loaders_mods_swap.get(loader, {}).items():
            if kv[0] in dependencies:
                dependencies.remove(kv[0])
                dependencies.add(kv[1])
        dependencies = sorted(dependencies)
        if dependencies:
            if world:
                print('The project has dependencies, unfortunately, it is not possible to install them in a WORLD command mode')
                print('You have install them manually: ' + ', '.join(dependencies))
            else:
                dependencies = [d for d in dependencies if not is_installed(d)]
                if dependencies:
                    print('Installation of dependencies: ' + ', '.join(dependencies))
                    for d in dependencies:
                        if install_project_file(directory, data, d):
                            installed = True
        
        return installed
    
    return False


def project_uninstall(directory, urlslug, world=None):
    urlslug = urlslug.lower()
    data = MCSMP(directory)
    test_version(directory, data)
    
    if world:
        for type, pt in project_types_world.items():
            if world in data[type] and urlslug in data[type][world]:
                path_filename = join(data.path, 'saves', world, pt.folder, data[type][world][urlslug])
                path_enable(data, type, urlslug, True, world)
                safe_del(path_filename)
                
                del data[type][world][urlslug]
                data.commit()
                print(f'Project {urlslug!r} deleted from {directory!r}')
                return
        
        print(f'The project {urlslug!r} is not installed in the world {world!r} of {directory!r}')
    
    else:
        for type, pt in project_types.items():
            if urlslug in data[type]:
                path_filename = join(data.path, pt.folder, data[type][urlslug])
                path_enable(data, type, urlslug, True)
                safe_del(path_filename)
                
                del data[type][urlslug]
                data.commit()
                print(f'Project {urlslug!r} deleted from {directory!r}')
                return
        
        print(f'The project {urlslug!r} is not installed in {directory!r}')


def project_enable(directory, urlslug, enable, world=None):
    urlslug = urlslug.lower()
    data = MCSMP(directory)
    
    if world:
        for type in project_types_world:
            if world in data[type] and urlslug in data[type][world]:
                path_enable(data, type, urlslug, enable, world)
                if enable:
                    print(f'Project {urlslug!r} in the world {world!r} of {directory!r} is now enabled')
                else:
                    print(f'Project {urlslug!r} in the world {world!r} of {directory!r} is now disabled')
                return
        
        print(f'The project {urlslug!r} is not installed in the world {world!r} of {directory!r}')
    
    else:
        for type in project_types:
            if urlslug in data[type]:
                path_enable(data, type, urlslug, enable)
                if enable:
                    print(f'Project {urlslug!r} in {directory!r}  is now enabled')
                else:
                    print(f'Project {urlslug!r} in {directory!r} is now disabled')
                return
    
        print(f'The project {urlslug!r} is not installed in {directory!r}')


def open_directory(directory, world=None):
    data = MCSMP(directory)
    if world:
        if world in data.datapack:
            join(data.path, 'saves', world)
        else:
            print(f'No world {world!r} in directory "{directory!r}. Opening the directory folder instead.')
    
    os.startfile(data.path)


def project_info(urlslug):
    urlslug = urlslug.lower()
    urllink = link('project', urlslug)
    url = requests.get(urllink)
    if url.ok:
        data = json.loads(url.content)
        try:
            datapack = json.loads(requests.get(link('project', urlslug, 'version'), params={'loaders':'["datapack"]'}).content)
        except Exception:
            datapack = []
        
        data_display = data['title'] + ' ' + (data['project_type'] if not datapack else 'datapack')
        print('+-'+'-'*(len(data_display))+'-+')
        print('| ' + data_display + ' |')
        print('+-'+'-'*(len(data_display))+'-+')
        if data['status'] == 'archived':
            print('<< ARCHIVED >>'.center(len(data_display)+4, '='))
        print()
        
        def clear_date(date):
            if '.' in date:
                date = date[:date.find('.')]
            return date
        published = clear_date(data['published'])
        updated = clear_date(data['updated'])
        print(data['description'])
        print(
            f"\nThe {data_display} was published on {published}, and was last updated on {updated},\nit has {data['downloads']} downloads and has {data['followers']} followers.")
        print("\nCategories:")
        for i in data['categories']:
            print('    ' + i)
        if data['additional_categories']:
            print("\nAdditional categories:")
            for i in data['additional_categories']:
                print('    ' + i)
        
        print("\nWays to donate:")
        for i in data['donation_urls']:
            print(f'    {i["platform"]}: {i["url"]}')
        print('\n\n-- DATA  --------------------------------')
        print(f"License: {data['license']['name']}")
        print(f"Serverside: {data['server_side']}")
        print(f"Clientside: {data['client_side']}")
        print('\n\n-- LINKS --------------------------------')
        print(f"Modrinth: https://modrinth.com/{data['project_type']}/{data['slug']}")
        print(f'Source: {data["source_url"]}')
        print(f'Discord: {data["discord_url"]}')
        print(f'Wiki: {data["wiki_url"]}')
    else:
        print(f"Error during url request, the project {urlslug} probably doesn't exist")

def project_versions_list(urlslug):
    urlslug = urlslug.lower()
    urllink = link('project', urlslug, 'version')
    url = requests.get(urllink)
    if url.ok:
        lst_version = json.loads(url.content)
        
        msg = f'Versions for: {urlslug}'
        print('+'+'-'*(len(msg)+2)+'+')
        print('| ' + msg + ' |')
        print('+'+'-'*(len(msg)+2)+'+')
        print()
        print('Available version:', len(lst_version))
        print()
        lst = []
        number_max = 0
        mc_max = 0
        loader_max = 0
        for e in lst_version:
            version_number = e['version_number']
            if len(e['game_versions']) == 1:
                game_versions = e['game_versions'][0]
            else:
                game_versions = e['game_versions'][0] + '-' + e['game_versions'][-1]
            loaders = ', '.join(e['loaders'])
            lst.append((version_number, game_versions, loaders))
            if len(version_number) > number_max:
                number_max = len(version_number)
            if len(game_versions) > mc_max:
                mc_max = len(game_versions)
            if len(loaders) > loader_max:
                loader_max = len(loaders)
        
        for e in lst:
            print(
                e[0] + ' '*(number_max-len(e[0])),
                '|',
                'Minecraft:', e[1] + ' '*(mc_max-len(e[1])),
                '|',
                'Loaders:', e[2] + ' '*(loader_max-len(e[2])),
            )
        
    else:
        print(f"Error during url request, the project {urlslug} probably doesn't exist")

def project_version_info(urlslug, version):
    urlslug = urlslug.lower()
    urllink = link('project', urlslug, 'version')
    url = requests.get(urllink)
    if url.ok:
        lst_version = json.loads(url.content)
        
        version_data = None
        for e in lst_version:
            if e['version_number'] == version:
                version_data = e
                break
        
        if not version_data:
            print(f"Error durg retreving info version, the {version!r} of the project {urlslug} doesn't exist")
            return
        
        msg1 = f"Project: {urlslug}"
        msg2 = f"Version: {version}"
        if len(msg1) > len(msg2):
            max = len(msg1)
        else:
            max = len(msg2)
        print('+'+'-'*(max+2)+'+')
        print('| ' + msg1 +' '*(max-len(msg1)) + ' |')
        print('| ' + msg2 +' '*(max-len(msg2)) + ' |')
        print('+'+'-'*(max+2)+'+')
        print()
        if len(version_data['game_versions']) == 1:
            game_versions = version_data['game_versions'][0]
        else:
            game_versions = version_data['game_versions'][0] + '-' + e['game_versions'][-1]
        
        print('Version name:', version_data['name'])
        print('Minecraft supported:', game_versions)
        print('Loader supported:', ', '.join(version_data['loaders']))
        print()
        print('Files:')
        for f in version_data['files']:
            filename = f['filename']
            print(f'"{filename}"', '| sha1:', f['hashes']['sha1'])
        
        
    else:
        print(f"Error during url request, the project {urlslug} probably doesn't exist")

def print_api(base_url, args=None):
    params = {}
    for p in args or []:
        if '=' not in p:
            params[p.replace(' ', '').strip()] = ''
        else:
            q,p = tuple(p.split('=',1))
            q = q.replace(' ', '').strip()
            p = p.replace(' ', '').strip()
            if q == 'facets':
                p = p.replace('"','').strip('[]').split('],[')
                for i in range(len(p)):
                    p[i] = '"'+ '","'.join(p[i].split(',')) +'"'
                p = '[['+ '],['.join(p) +']]'
                params[q] = p
            elif q in ['categories','display_categories','game_versions','loaders','ids','versions','gallery','hashes','primary_file','file_parts']:
                p = p.replace('"','').strip('[]').split(',')
                p = '["'+ '","'.join(p) +'"]'
                params[q] = p
            else:
                params[q] = p
    
    urllink = link(base_url)
    url = requests.get(urllink, params=params)
    if not url.ok:
        print(f"<error: {urllink} >")
    else:
        print(json.dumps(json.loads(url.content), indent=2))
    pass

## argparse
parser = argparse.ArgumentParser(
    description='Simple Modrinth Project Manager for Minecraft',
)
subparsers = parser.add_subparsers(
    title='commands to execute',
    metavar='<command>',
    dest='command',
    required=True,
    description='In most case, the command take the form: <command> DIRECTORY PROJECT [WORLD]',
)

def buid_parser(
    command: str,
    help: str,
    description: str=None,
    directory: bool=False,
    project: bool=False,
    world: bool=False,
):
    if not description:
        description = help[:1].upper()+help[1:]
    
    parser = subparsers.add_parser(
        name=command,
        help='- '+help,
        description=description,
    )
    
    if directory:
        parser.add_argument('directory', metavar='DIRECTORY', type=str, help='name of the target directory')
    if project:
        parser.add_argument('project', metavar='PROJECT', type=str, help='slug of the target project')
    if world:
        parser.add_argument('world', metavar='WORLD', type=str, nargs='?', help='specific world to target')
    
    return parser


# global
args_list = buid_parser(
    command='list',
    help='show all directory or project of a directory',
    description='Show configured directory or installed projects in a specified directory',
)
args_list.add_argument('directory', metavar='DIRECTORY', type=str, nargs='?', help='dispaly the projects for this directory')
args_list.add_argument('world', metavar='WORLD', type=str, nargs='?', help='dispaly the datapacks for this world')

# directory setting
args_directory_add = buid_parser(
    command='directory-add',
    help='adding a configured directory',
    description='Add a directory a minecraft folder that will be contain mods, resourcepacks and datapacks',
)
args_directory_add.add_argument('directory', metavar='DIRECTORY', type=str, help='name of the directory')
args_directory_add.add_argument('path', metavar='PATH', type=str, help='target path of the directory, must the root of a /.minecraft/ folder')

args_directory_remove = buid_parser(
    command='directory-remove',
    help='remove a configured directory',
    description='Remove a configured directory from the setting',
)
args_directory_add.add_argument('directory', metavar='DIRECTORY', type=str, help='name of a directory')

args_version = buid_parser(
    command='version',
    help='Minecraft version for a directory',
    description='Show or edit the Minecraft version for a directory',
    directory=True,
)
args_version.add_argument('id', metavar='ID', type=str, nargs='?', help='id of the new target version of Minecraft to set')

args_loader = buid_parser(
    command='loader',
    help='Loader for a directory',
    description='Show or edit the Loader used for a directory',
    directory=True,
)
args_loader.add_argument('id', metavar='ID', type=str, nargs='?', help='id of the new target Loader to set')

args_loader = buid_parser(
    command='shader',
    help='Shader loader for a directory',
    description='Show or edit the Shader loader used for a directory',
    directory=True,
)
args_loader.add_argument('id', metavar='ID', type=str, nargs='?', help='id of the new target Shader loader to set')

# manage project's
buid_parser(
    command='check',
    help='check if the project is installed',
    directory=True,
    project=True,
    world=True,
)
buid_parser(
    command='install',
    help='install/update a project',
    directory=True,
    project=True,
    world=True,
)
buid_parser(
    command='enable',
    help='enable a project',
    directory=True,
    project=True,
    world=True,
)
buid_parser(
    command='disable',
    help='disable a project',
    directory=True,
    project=True,
    world=True,
)
buid_parser(
    command='uninstall',
    help='uninstall a project',
    directory=True,
    project=True,
    world=True,
)
buid_parser(
    command='update',
    help='update all projects in a directory or for a world',
    directory=True,
    world=True,
)
buid_parser(
    command='open',
    help='open the folder of a directory',
    directory=True,
    world=True,
)

# utility
args_info = buid_parser(
    command='info',
    help='list various info about a project',
    project=True,
)
args_info_group = args_info.add_mutually_exclusive_group()
args_info_group.add_argument('--list-versions', action='store_true', help='list all versions availide')
args_info_group.add_argument('--version', metavar='VERSION', type=str, help='show the info for a specific version')

args_api = buid_parser(
    command='api',
    help='print a API request',
    description='Print a API request',
)
args_api.add_argument('url', metavar='URL', type=str, help='url of the API request')
args_api.add_argument('--', dest='params', metavar='PARAMS', type=str, nargs='+', default=[], help='parameters to apply to the API request')

args_clear_cache = buid_parser(
    command='clear-cache',
    help='clear the cache',
    description='Clear the cache, or specific cache files',
)
args_clear_cache.add_argument('files', metavar='FILES', type=str, nargs='*', default=[], help='specific cache files to remove')


def main():
    args = parser.parse_args()
    
    if args.command == 'list':
        if args.world is not None:
            list_world_projects(args.directory, args.world)
        elif args.directory is not None:
            list_projects(args.directory)
        else:
            list_directorys()
    elif args.command == 'directory-add':
        directory_add(args.directory, args.path)
    elif args.command == 'directory-remove':
        directory_remove(args.directory)
    
    elif args.command == 'version':
        directory_version(args.directory, args.id)
    elif args.command == 'loader':
        directory_loader(args.directory, args.id)
    elif args.command == 'shader':
        directory_shader(args.directory, args.id)
    
    elif args.command == 'check':
        project_check(args.directory, args.project, args.world)
    elif args.command == 'install':
        project_install(args.directory, args.project, args.world)
    elif args.command == 'enable':
        project_enable(args.directory, args.project, True, args.world)
    elif args.command == 'disable':
        project_enable(args.directory, args.project, False, args.world)
    elif args.command == 'uninstall':
        project_uninstall(args.directory, args.project, args.world)
    elif args.command == 'update':
        project_update(args.directory, args.world)
    elif args.command == 'open':
        open_directory(args.directory, args.world)
    
    elif args.command == 'info':
        if args.list_versions:
            project_versions_list(args.project)
        elif args.version:
            project_version_info(args.project, args.version)
        else:
            project_info(args.project)
    elif args.command == 'api':
        print_api(args.url, args.params)
    elif args.command == 'clear-cache':
        Cache.clear_cache(args.files)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
