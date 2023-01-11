from sys import argv
import os
import json
from collections import namedtuple

import requests
requests = requests.Session()
requests.headers.update({'User-Agent':'un-pogaz/MC-Modrinth-Project-Manager (un.pogaz@gmail.com)'})


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

def _mcsmp(path):
    return os.path.join(path, '.mcsmp.json')
def mcsmp(dir, data=None):
    path = root().get(dir, None)
    
    if not path:
        print(f'The directory "{dir}" his not defined')
        exit()
    
    if not os.path.exists(path):
        print(f'The path "{path}" of the directory "{dir}" doesn\'t exist')
        exit()
    
    edited = False
    data_path = _mcsmp(path)
    if data is not None:
        edited = True
    else:
        if not os.path.exists(data_path):
            data = {}
            edited = True
        else:
            data = _json(data_path)
    
    for k in ['game_version', 'loader']:
        if k not in data:
            data[k] = None
            edited = True
    for k in list(project_types.keys()) + list(project_types_world.keys()):
        if k not in data:
            data[k] = {}
            edited = True
        
        data[k] = sort_dict(data[k])
    
    for k in project_types_world.keys():
        for kk in list(data[k].keys()):
            w = data[k][kk]
            if w:
                data[k][kk] = sort_dict(w)
            else:
                del data[k][kk]
                edited = True
    
    if edited:
        if data and 'path' in data: del data['path']
        _json(data_path, data)
    
    data['path'] = path
    return data

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
    except:
        pass

class Cache:
    _cachedir = os.path.join(os.path.dirname(argv[0]), '.cache')
    def _make_cachedir():
        cache_version = os.path.join(Cache._cachedir, '.v1')
        if not os.path.exists(cache_version):
            Cache.clear_cache()
        
        if not os.path.exists(Cache._cachedir):
            os.makedirs(Cache._cachedir, exist_ok=True)
            with open(cache_version, 'wt', newline='\n', encoding='utf-8') as f:
                f.write('')
    
    def clear_cache(files=None):
        if files:
            for f in files:
                safe_del(os.path.join(Cache._cachedir, f))
            
            print('Cache files cleaned: ' + ', '.join(files))
        else:
            safe_del(Cache._cachedir)
            if files is not None:
                print('Cache folder cleaned')
    
    
    _project = None
    _project_path = os.path.join(_cachedir, 'project')
    
    def _read_project():
        if not Cache._project:
            Cache._project = _json(Cache._project_path)
    
    def add_project(id, slug):
        Cache._read_project()
        if id not in Cache._project:
            Cache._project[id] = slug
            Cache._make_cachedir()
            _json(Cache._project_path, Cache._project)
    
    def get_project(id):
        Cache._read_project()
        return Cache._project.get(id, None)
    
    
    _version = None
    _version_path = os.path.join(_cachedir, 'version')
    
    def _read_version():
        if not Cache._version:
            Cache._version = _json(Cache._version_path)
    
    def add_version(id, slug):
        Cache._read_version()
        if id not in Cache._version:
            Cache._version[id] = slug
            Cache._make_cachedir()
            _json(Cache._version_path, Cache._version)
    
    def get_version(id):
        Cache._read_version()
        return Cache._version.get(id, None)
    
    
    _slug = None
    _slug_path = os.path.join(_cachedir, 'slug')
    
    def _read_slug():
        if not Cache._slug:
            Cache._slug = _json(Cache._slug_path)
    
    def add_slug(slug, id, type):
        Cache._read_slug()
        if slug not in Cache._slug:
            Cache._slug[slug] = {'id':id,'project_type':type}
            Cache._make_cachedir()
            _json(Cache._slug_path, Cache._slug)
    
    def get_slug(slug):
        Cache._read_slug()
        return Cache._slug.get(slug, None)

hash_algo = 'sha1'
def hash_file(path):
    import hashlib
    
    if os.path.exists(path):
        algo = hashlib.new(hash_algo)
        
        with open(path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                algo.update(data)
        
        return algo.hexdigest()



def dir_add(dir, path):
    path = os.path.abspath(path).replace('\\', '/')
    if not os.path.exists(path):
        print(f'The path "{path}" doesn\'t exist')
        exit()
    
    if not os.path.isdir(path):
        print(f'The path "{path}" is not a folder')
        exit()
    
    r = root()
    for k,v in r.items():
        if path == v and dir != k:
            print(f'The path "{path}" is already assosiated to the directory "{k}"')
            exit()
    
    path_old = r.get(dir, None)
    r[dir] = path
    root(r)
    
    if path_old and path_old != path:
        _json(_mcsmp(path), _json(_mcsmp(path_old)))
        os.remove(_mcsmp(path_old))
    
    data = mcsmp(dir)
    
    print(f'Directorie "{dir}" added')
    if not data['game_version'] and not data['loader']:
        print(f"Don't forget to set a 'version' for Minecraft and a 'loader'")
    elif not data['game_version']:
        print(f"Don't forget to set a 'version' for Minecraft")
    elif not data['loader']:
        print(f"Don't forget to set a 'loader'")


def dir_version(dir, version):
    data = mcsmp(dir)
    data['game_version'] = version
    print(f'Directorie "{dir}" set to the version {version}')
    mcsmp(dir, data)

def dir_loader(dir, loader):
    data = mcsmp(dir)
    data['loader'] = loader.lower()
    print(f'Directorie "{dir}" set to the loader {loader}')
    mcsmp(dir, data)


def test_version(dir, data, _exit=True):
    if not data['game_version']:
        print(f'The directory "{dir}" has no defined version')
        if _exit: exit()
        else: return False
    return True

def test_loader(dir, data, _exit=True):
    test_version(dir, data)
    if not data['loader']:
        print(f'The directory "{dir}" has no defined loader')
        if _exit: exit()
        else: return False
    return True

def test_world(dir, data, world, _exit=True):
    test_version(dir, data)
    if not os.path.exists(os.path.join(data['path'], 'saves', world)):
        print(f'The directory "{dir}" has no world named "{world}"')
        if _exit: exit()
        else: return False
    return True


ProjectType = namedtuple('ProjectType', 'folder test')
project_types = {
    'resourcepack':ProjectType('resourcepacks', test_version),
    'mod':ProjectType('mods', test_loader),
    'shader':ProjectType('shaderpacks', test_version),
}
project_types_world = {
    'datapack':ProjectType('datapacks', test_world),
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


def project_list(dir, world=None):
    
    def print_basic(name, data):
        path = data['path']
        loader = data['loader']
        game_version = data['game_version']
        print(f'"{name}" : {game_version}/{loader} => "{path}"')
    
    if dir is None:
        r = root()
        if not r:
            print(f'No directorys has defined')
            return
        for name in r:
            print_basic(name, mcsmp(name))
    
    if dir is not None:
        data = mcsmp(dir)
        print_basic(dir, data)
        
        if world:
            test_world(dir, data, world)
            for type, pt in project_types_world.items():
                if pt.test(dir, data, world, False):
                    if world in data[type] and data[type][world]:
                        world_path = os.path.join(data['path'], 'saves', world, pt.folder)
                        print()
                        print(f'--== Installed {pt.folder} in the world "{world}" ==--')
                        for urlslug in data[type][world]:
                            enabled, present = test_filename(os.path.join(world_path, data[type][world][urlslug]))
                            print(f"{urlslug}" + get_print_filename(enabled, present))
        
        else:
            for type, pt in project_types.items():
                if data[type] and pt.test(dir, data, False):
                    print()
                    print(f'--== Installed {pt.folder} ==--')
                    for urlslug in data[type]:
                        enabled, present = test_filename(os.path.join(data['path'], pt.folder, data[type][urlslug]))
                        print(f"{urlslug}" + get_print_filename(enabled, present))

def project_check(dir, urlslug, world=None):
    urlslug = urlslug.lower()
    data = mcsmp(dir)
    test_version(dir, data)
    
    if world:
        test_world(dir, data, world)
        for type, pt in project_types_world.items():
            if world in data[type]:
                world_path = os.path.join(data['path'], 'saves', world, pt.folder)
                if urlslug in data[type][world]:
                    enabled, present = test_filename(os.path.join(world_path, data[type][world][urlslug]))
                    print(f'"{urlslug}" is installed in the world "{world}" of the directory "{dir}"'+ get_print_filename(enabled, present))
                    if not present:
                        print(f'but the file are not present! Reinstal the project')
                    return
                
        print(f'"{urlslug}" is not installed in the world "{world}" of the directory "{dir}"')
    
    else:
        for type, pt in project_types.items():
            if urlslug in data[type]:
                enabled, present = test_filename(os.path.join(data['path'], pt.folder, data[type][urlslug]))
                print(f'"{urlslug}" is installed in the directory "{dir}"'+ get_print_filename(enabled, present))
                if not present:
                    print(f'but the file are not present! Reinstal the project')
                return
    
        print(f'"{urlslug}" is not installed in the directory "{dir}"')


def path_disabled(path):
    return path+'.disabled'
def path_enable(data, type, urlslug, enable, world=None):
    urlslug = urlslug.lower()
    if world:
        path_filename = os.path.join(data['path'], 'saves', world, project_types_world[type].folder, data[type][world][urlslug])
    else:
        path_filename = os.path.join(data['path'], project_types[type].folder, data[type][urlslug])
    
    if enable and os.path.exists(path_disabled(path_filename)):
        os.rename(path_disabled(path_filename), path_filename)
    
    if not enable and os.path.exists(path_filename):
        os.rename(path_filename, path_disabled(path_filename))


def link(*wanted):
    return f'https://api.modrinth.com/v2/' + '/'.join(wanted)

def project_install(dir, urlslug, world=None):
    data = mcsmp(dir)
    if install_project_file(dir, data, urlslug, world):
        mcsmp(dir, data)

def project_update(dir, world=None):
    data = mcsmp(dir)
    
    total = []
    errors = []
    
    if world:
        for type, pt in project_types_world.items():
            if pt.test(dir, data, world, False):
                if world in list(data[type].keys()):
                    for urlslug in data[type][world]:
                        rslt = install_project_file(dir, data, urlslug, world)
                        if rslt is None:
                            errors.append(urlslug)
                        if rslt:
                            total.append(urlslug)
                            mcsmp(dir, data)
                        print()
        
        print(f'Finaly! {len(total)} projects has been updated in the world "{world}" of "{dir}"')
    
    else:
        for type, pt in project_types.items():
            if pt.test(dir, data, False):
                for urlslug in list(data[type].keys()):
                    rslt = install_project_file(dir, data, urlslug)
                    if rslt is None:
                        errors.append(urlslug)
                    if rslt:
                        total.append(urlslug)
                        mcsmp(dir, data)
                    print()
        
        print(f'Finaly! {len(total)} projects has been updated in "{dir}"')
    
    if total:
        print('Updated projects: ' + ', '.join(total))
    if errors:
        print(f'but... the following projects have suffered an error during their download:')
        print(', '.join(errors))

def install_project_file(dir, data, urlslug, world=None):
    urlslug = urlslug.lower()
    game_version = data['game_version']
    loader = data['loader']
    
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
            print(f"The project {urlslug} has a type '{project_type}' incompatible with the argument [World]")
            return False
        
        pt = project_types_world[project_type]
        pt.test(dir, data, world)
        base_path = os.path.join(data['path'], 'saves', world, pt.folder)
    else:
        
        if project_type not in project_types:
            print(f"The project {urlslug} has a type '{project_type}' incompatible for a global install")
            return False
        
        pt = project_types[project_type]
        pt.test(dir, data)
        base_path = os.path.join(data['path'], pt.folder)
    
    print(f"Fetching versions of {urlslug} for Minecraft '{game_version}' and the loader '{loader}'...")
    
    if project_type == 'resourcepack':
        loader = 'minecraft'
    if project_type == 'shader':
        loader = ''
    if project_type == 'datapack':
        loader = 'datapack'
    
    if loader:
        all_loaders = [loader]+loaders_alt.get(loader, [])
    else:
        all_loaders = []
    
    params = {'game_versions':f'["{game_version}"]', 'loaders':'['+','.join(['"'+l+'"' for l in all_loaders])+']'}
    versions = json.loads(requests.get(link('project', project_id, 'version'), params=params).content)
    
    version_project = None
    if all_loaders:
        for _loader in all_loaders:
            for v in versions:
                if _loader in v['loaders']:
                    version_project = v
                    break
            if version_project:
                break
    else:
        version_project = versions[0]
    
    if not version_project:
        print(f"No version available")
    
    else:
        Cache.add_version(version_project['id'], urlslug)
        version_file = version_project['files'][0]
        
        if project_type == 'shader' and version_project['loaders'][0] in ['vanilla', 'canvas']:
            base_path = os.path.join(data['path'], 'resourcepacks')
        
        os.makedirs(base_path, exist_ok=True)
        
        filename = version_file['filename']
        if world:
            filename_old = data[project_type].get(world, {}).get(urlslug, None)
        else:
            filename_old = data[project_type].get(urlslug, None)
        path_filename = os.path.join(base_path, filename)
        
        print(f"Got the link for '{filename}'")
        
        disabled = False
        if os.path.exists(path_disabled(path_filename)):
            disabled = True
            os.rename(path_disabled(path_filename), path_filename)
        
        if filename_old:
            path_filename_old = os.path.join(base_path, filename_old)
            if os.path.exists(path_disabled(path_filename_old)):
                disabled = True
                os.rename(path_disabled(path_filename_old), path_filename_old)
            
        installed = False
        if filename_old and os.path.exists(path_filename) and filename_old == filename and hash_file(path_filename) == version_file['hashes'][hash_algo]:
            if world:
                print(f'The project {urlslug} is already up to date in the world "{world}" of "{dir}"')
            else:
                print(f'The project {urlslug} is already up to date in "{dir}"')
        
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
                try:
                    os.remove(path_filename_old)
                except:
                    pass
            
            if world:
                if world not in data[project_type]:
                    data[project_type][world] = {}
                data[project_type][world][urlslug] = filename
                print(f'Done! The project "{urlslug}" has been installed in the world "{world}" of "{dir}"')
            else:
                data[project_type][urlslug] = filename
                print(f'Done! The project "{urlslug}" has been installed in "{dir}"')
            installed = True
        
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
            except:
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
                        if install_project_file(dir, data, d):
                            installed = True
        
        return installed
    
    return False


def project_remove(dir, urlslug, world=None):
    urlslug = urlslug.lower()
    data = mcsmp(dir)
    test_version(dir, data)
    
    if world:
        for type, pt in project_types_world.items():
            if world in data[type] and urlslug in data[type][world]:
                path_filename = os.path.join(data['path'], 'saves', world, pt.folder, data[type][world][urlslug])
                path_enable(data, type, urlslug, True, world)
                try:
                    os.remove(path_filename)
                except:
                    pass
                
                del data[type][world][urlslug]
                mcsmp(dir, data)
                print(f'Project {urlslug} deleted from "{dir}"')
                return
        
        print(f'The project {urlslug} is not installed in the world "{world}" of "{dir}"')
    
    else:
        for type, pt in project_types.items():
            if urlslug in data[type]:
                path_filename = os.path.join(data['path'], pt.folder, data[type][urlslug])
                path_enable(data, type, urlslug, True)
                try:
                    os.remove(path_filename)
                except:
                    pass
                
                del data[type][urlslug]
                mcsmp(dir, data)
                print(f'Project {urlslug} deleted from "{dir}"')
                return
        
        print(f'The project {urlslug} is not installed in "{dir}"')


def project_enable(dir, urlslug, enable, world=None):
    urlslug = urlslug.lower()
    data = mcsmp(dir)
    
    if world:
        for type in project_types_world:
            if world in data[type] and urlslug in data[type][world]:
                path_enable(data, type, urlslug, enable, world)
                if enable:
                    print(f'Project {urlslug} in the world "{world}" of "{dir}" is now enabled')
                else:
                    print(f'Project {urlslug} in the world "{world}" of "{dir}" is now disabled')
                return
        
        print(f'The project {urlslug} is not installed in the world "{world}" of "{dir}"')
    
    else:
        for type in project_types:
            if urlslug in data[type]:
                path_enable(data, type, urlslug, enable)
                if enable:
                    print(f'Project {urlslug} in "{dir}" is now enabled')
                else:
                    print(f'Project {urlslug} in "{dir}" is now disabled')
                return
    
        print(f'The project {urlslug} is not installed in "{dir}"')



def project_info(urlslug):
    urlslug = urlslug.lower()
    urllink = link('project', urlslug)
    url = requests.get(urllink)
    if url.ok:
        data = json.loads(url.content)
        try:
            datapack = json.loads(requests.get(link('project', urlslug, 'version'), params={'loaders':'["datapack"]'}).content)
        except:
            datapack = []
        
        data_display = data['title'] + ' ' + (data['project_type'] if not datapack else 'datapack')
        print('+'+'-'*(len(data_display)+2)+'+')
        print('| ' + data_display + ' |')
        print('+'+'-'*(len(data_display)+2)+'+\n')

        print(data['description'])
        print(
            f"\nThe {data_display} was published on {data['published']}, and was last updated on {data['updated']},\nit has {data['downloads']} downloads and has {data['followers']} followers.")
        print("\nCategories:")
        for i in data['categories']:
            print('    ' + i)
            
        print("\nWays to donate:")
        for i in data['donation_urls']:
            print(f'    {i["platform"]}: {i["url"]}')
        print('\n\n-- DATA  --------------------------------')
        print(f"License: {data['license']['name']}")
        print(f"Serverside: {data['server_side']}")
        print(f"Clientside: {data['client_side']}")
        print('\n\n-- LINKS --------------------------------')
        print(f'Source: {data["source_url"]}')
        print(f'Discord: {data["discord_url"]}')
        print(f'Wiki: {data["wiki_url"]}')
    else:
        print(f"Error during url request, the project {urlslug} probably doesn't exist")

def print_api(base_url, args):
    params = {}
    if '--' in args:
        idx = args.index('--')
        for p in args[idx+1:]:
            if not '=' in p:
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



def usage():
    print(os.path.basename(argv[0]) + " <CMD> [DIR [PROJECT]] [[WORLD]]")
    print()
    print("Commands:")
    print("    list [DIR]           - show all installed projects in specified directory (mods, resourcepacks and datapacks)")
    print("                         - if no DIR specified, show all defined directory")
    print()
    print("    add <DIR> <PATH>         - add a directory, the target path must the root .minecraft folder")
    print("    version <DIR> <ID>       - set Minecraft version of a directory")
    print("    loader <DIR> <ID>        - define the loader of the directory")
    print()
    print("    check <DIR> <PROJECT>        - check if the project is installed")
    print("    install <DIR> <PROJECT>      - install/update a project")
    print("    enable <DIR> <PROJECT>       - enable a project")
    print("    disable <DIR> <PROJECT>      - disable a project")
    print("    remove <DIR> <PROJECT>       - remove a project")
    print("    update <DIR>                 - update all projects in a directory")
    print()
    print("    info <PROJECT>               - show info about a project")
    print("    api URL [-- PARAMS ...]]     - print a API request")
    print("    clear-cache [FILE ...]]     - clear the cache, or specific cache files")
    print()
    print("DIR is the target directory to manage")
    print("PROJECT is the slug-name of the wanted project")
    print("WORLD is to target a specific world (datapack), always at the end (last argument)")
    exit()


def get_arg_n(idx, required=True):
    if len(argv) <= idx:
        if required:
            usage()
        else:
            return None
    return argv[idx]

def main():
    cmd = get_arg_n(1).lower()
    if False: pass
    
    elif cmd == 'list':
        project_list(get_arg_n(2, False), get_arg_n(3, False))
        
    elif cmd == 'add':
        dir_add(get_arg_n(2), get_arg_n(3))
    elif cmd == 'version':
        dir_version(get_arg_n(2), get_arg_n(3))
    elif cmd == 'loader':
        dir_loader(get_arg_n(2), get_arg_n(3))
    
    elif cmd == 'check':
        project_check(get_arg_n(2), get_arg_n(3), get_arg_n(4, False))
    elif cmd == 'install':
        project_install(get_arg_n(2), get_arg_n(3), get_arg_n(4, False))
    elif cmd == 'enable':
        project_enable(get_arg_n(2), get_arg_n(3), True, get_arg_n(4, False))
    elif cmd == 'disable':
        project_enable(get_arg_n(2), get_arg_n(3), False, get_arg_n(4, False))
    elif cmd == 'remove':
        project_remove(get_arg_n(2), get_arg_n(3), get_arg_n(4, False))
    elif cmd == 'update':
        project_update(get_arg_n(2), get_arg_n(3, False))
    
    elif cmd == 'info':
        project_info(get_arg_n(2))
    elif cmd == 'api':
        print_api(get_arg_n(2), argv[3:])
    elif cmd == 'clear-cache':
        Cache.clear_cache(argv[2:])
    else:
        usage()

if __name__ == "__main__":
    main()