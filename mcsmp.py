from os.path import exists
from sys import argv, path

import os
import json
from collections import namedtuple

import requests


def _json(path ,data=None):
    if data:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    else:
        try:
            return json.loads(open(path).read())
        except:
            return {}

def mcsmp(data=None):
    return _json('mcsmp.json', data)


def dir_add(dir, path):
    path = os.path.abspath(path)
    
    data = mcsmp()
    if dir not in data:
        data[dir] = {}
    data[dir]['path'] = path.replace('\\','/')
    data[dir]['game_version'] = data[dir].get('game_version', None)
    data[dir]['loader'] = data[dir].get('loader', None)
    data[dir]['resourcepack'] = data[dir].get('resourcepack', {})
    data[dir]['mod'] = data[dir].get('mod', {})
    print(f'Directorie "{dir}" added')
    if not data[dir]['game_version'] and not data[dir]['loader']:
        print(f"Don't forget to set a 'version' for Minecraft and a 'loader'")
    elif not data[dir]['game_version']:
        print(f"Don't forget to set a 'version' for Minecraft")
    elif not data[dir]['loader']:
        print(f"Don't forget to set a 'loader'")
    
    mcsmp(data)

def dir_list():
    data = mcsmp()
    if not data:
        print(f'No directories has defined')
        return
    for dir, data in mcsmp().items():
        path = data['path']
        loader = data['loader']
        game_version = data['game_version']
        print(f'"{dir}" : {game_version}/{loader} => "{path}"')

def dir_version(dir, version):
    data = mcsmp()
    test_dir(data, dir)
    data[dir]['game_version'] = version
    print(f'Directorie "{dir}" set to the version {version}')
    mcsmp(data)

def dir_loader(dir, loader):
    data = mcsmp()
    test_dir(data, dir)
    data[dir]['loader'] = loader.lower()
    print(f'Directorie "{dir}" set to the loader {loader}')
    mcsmp(data)

def test_dir(data, dir):
    if dir not in data:
        print(f'The directorie "{dir}" his not defined')
        exit()
    
    if not os.path.exists(data[dir]['path']):
        print(f'The path directorie "{dir}" doesn\'t exist')
        exit()

def test_version(data, dir):
    test_dir(data, dir)
    if not data[dir]['game_version']:
        print(f'The directorie "{dir}" has no defined version')
        exit()

def test_loader(data, dir):
    test_version(data, dir)
    if not data[dir]['loader']:
        print(f'The directorie "{dir}" has no defined loader')
        exit()


ProjectType = namedtuple('ProjectType', 'type folder test')
project_types = [
    ProjectType('resourcepack', 'resourcepacks', test_version),
    ProjectType('mod', 'mods', test_loader),
]
alt_loaders = {'quilt': ['fabric']}

def project_list(dir):
    data = mcsmp()
    first = True
    for pt in project_types:
        lst = data[dir][pt.type]
        if lst:
            first = False
            if not first: print()
            print(f'--== Installed {pt.folder} for "{dir}" ==--')
            for name, _ in data[dir][pt.type].items():
                print(f"{name}")


def project_check(dir, slug):
    data = mcsmp()
    test_version(data, dir)
    
    if slug in data[dir]['mod'] or slug in data[dir]['resourcepack']:
        print(f'"{slug}" is installed in the directorie "{dir}"')
    else:
        print(f'"{slug}" is not installed in the directorie "{dir}"')


def path_disabled(path):
    return path+'.disabled'
def path_enable(data, dir, folder, urlslug, enable):
    
    path_filename = os.path.join(data[dir]['path'], folder, data[dir]['mod'][urlslug])
    
    if enable and os.path.exists(path_disabled(path_filename)):
        os.rename(path_disabled(path_filename), path_filename)
    
    if not enable and os.path.exists(path_filename):
        os.rename(path_filename, path_disabled(path_filename))


def link(wanted):
    return f'https://api.modrinth.com/v2/{wanted}'

def project_install(dir, slug):
    data = mcsmp()
    
    install_project_file(data, dir, slug)
    
    mcsmp(data)

def project_update(dir):
    data = mcsmp()
    
    total = 0
    errors = []
    
    for slug in data[dir]['resourcepack']:
        rslt = install_project_file(data, dir, slug)
        if rslt is None:
            errors.append(slug)
        if rslt:
            total += 1
        print()
    
    for slug in data[dir]['mod']:
        rslt = install_project_file(data, dir, slug)
        if rslt is None:
            errors.append(slug)
        if rslt:
            total += 1
        print()
    
    print(f'Finaly! {total} projects has been updated in "{dir}"')
    if errors:
        print(f'but... the following projects have suffered an error during their download:')
        print(', '.join(errors))
    mcsmp(data)

def install_project_file(data, dir, urlslug):
    urlslug = urlslug.lower()
    urllink = link(f'project/{urlslug}')
    game_version = data[dir]['game_version']
    loader = data[dir]['loader']
    
    url = requests.get(urllink)
    if not url.ok:
        print(f"Error during url request, the project {urlslug} probably doesn't exist")
        return None
    
    if url.ok:
        project_data = json.loads(url.content)
        project_id = project_data['id']
        project_type = project_data['project_type']
        
        if project_type == 'resourcepack':
            loader = 'minecraft'
        
        base_path = None
        for pt in project_types:
            if project_type == pt.type:
                pt.test(data, dir)
                base_path = os.path.join(data[dir]['path'], pt.folder)
                os.makedirs(base_path, exist_ok=True)
        
        if not base_path:
            print(f"The project type of {urlslug} is unknow: {project_type}")
            return None
        
        print("Fetch versions")
        versions = json.loads(requests.get(f"https://api.modrinth.com/v2/project/{project_id}/version").content)
        
        version_project = None
        for _loader in [loader]+alt_loaders.get(loader, []):
            for v in versions:
                if game_version in v['game_versions'] and _loader in v['loaders']:
                    version_project = v['files'][0]
                    break
        
        if not version_project:
            print(f"No version of {urlslug} available for Minecraft {game_version} and the loader {loader}")
        
        if version_project:
            print(f"Got the link for Minecraft {game_version} and the loader {loader}")
            
            filename = version_project['filename']
            filename_old = data[dir][project_type].get(urlslug, None)
            path_filename = os.path.join(base_path, filename)
            
            disabled = False
            if os.path.exists(path_disabled(path_filename)):
                disabled = True
                os.rename(path_disabled(path_filename), path_filename)
            
            if filename_old:
                path_filename_old = os.path.join(base_path, filename_old)
                if os.path.exists(path_disabled(path_filename_old)):
                    disabled = True
                    os.rename(path_disabled(path_filename_old), path_filename_old)
                
                if os.path.exists(path_filename_old) and filename_old == filename:
                    print(f"The project {urlslug} is already up to date")
            
            installed = False
            if not os.path.exists(path_filename) or not filename_old:
                if not os.path.exists(path_filename):
                    print("Download project now...")
                    with open(path_filename, 'wb') as f:
                        f.write(requests.get(version_project['url']).content)
                
                if filename_old and filename_old != filename:
                    try:
                        os.remove(path_filename_old)
                    except:
                        pass
                    
                data[dir][project_type][urlslug] = filename
                print(f'Done! The project "{urlslug}" has been installed in "{dir}"')
                installed = True
            
            if disabled:
                os.rename(path_filename, path_disabled(path_filename))
            
            return installed
        
        return False


def project_remove(dir, urlslug):
    data = mcsmp()
    test_version(data, dir)
    urlslug = urlslug.lower()
    
    for pt in project_types:
        if urlslug in data[dir][pt.type]:
            path_filename = os.path.join(data[dir]['path'], pt.folder, data[dir]['mod'][urlslug])
            path_enable(data, dir, pt.folder, urlslug, True)
            try:
                os.remove(path_filename)
            except:
                pass
            
            del data[dir][pt.type][urlslug]
            mcsmp(data)
            print(f'Deleted project {urlslug} from "{dir}"')
            break
    
    print(f'The project {urlslug} is not installed in "{dir}"')


def project_enable(dir, urlslug, enable):
    data = mcsmp()
    test_version(data, dir)
    urlslug = urlslug.lower()
    
    for pt in project_types:
        if urlslug in data[dir][pt.type]:
            path_enable(data, dir, pt.folder, urlslug, enable)
            if enable:
                print(f'Project {urlslug} in "{dir}" is now enabled')
            else:
                print(f'Project {urlslug} in "{dir}" is now disabled')
            break
    
    print(f'The project {urlslug} is not installed in "{dir}"')



def project_info(urlslug):
    urlslug = urlslug.lower()
    urllink = link("project/"+urlslug)
    url = requests.get(urllink)
    if url.ok:
        data = json.loads(url.content)
        data_display = data['title'] + ' ' + data['project_type']
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


# mcsmp install fabric-18.2 sodium
# mcsmp <CMD> [<DIR> [<PROJECT>]]

def usage():
    print(os.path.basename(argv[0]) + " <CMD> [DIR [PROJECT]]")
    print()
    print("Commands:")
    print("    dirs                 - show all defined directory")
    print("    list <DIR>           - show all installed projects (mods, resourcepacks and datapacks)")
    print("    info <PROJECT>       - show info about a mod")
    print()
    print("    add <DIR> <PATH>         - add a directory, the target path must the root .minecraft folder")
    print("    version <DIR> <ID>       - set Minecraft version of a directory")
    print("    loader <DIR> <ID>        - define the loader of the directory")
    print()
    print("    check <DIR> <PROJECT>       - check if the project is installed")
    print("    install <DIR> <PROJECT>     - install/update a project")
    print("    enable <DIR> <PROJECT>      - enable a project")
    print("    disable <DIR> <PROJECT>     - disable a project")
    print("    remove <DIR> <PROJECT>      - remove a project")
    print("    update <DIR>                - update all projects in a directory")
    print()
    print("DIR is the target directory to manage")
    print("PROJECT is the slug-name of the wanted project")
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
    
    elif cmd == 'dirs':
        dir_list()
    elif cmd == 'list':
        project_list(get_arg_n(2))
    elif cmd == 'info':
        project_info(get_arg_n(2))
        
    elif cmd == 'add':
        dir_add(get_arg_n(2), get_arg_n(3))
    elif cmd == 'version':
        dir_version(get_arg_n(2), get_arg_n(3))
    elif cmd == 'loader':
        dir_loader(get_arg_n(2), get_arg_n(3))
    
    elif cmd == 'check':
        project_check(get_arg_n(2), get_arg_n(3))
    elif cmd == 'install':
        project_install(get_arg_n(2), get_arg_n(3))
    elif cmd == 'enable':
        project_enable(get_arg_n(2), get_arg_n(3), True)
    elif cmd == 'disable':
        project_enable(get_arg_n(2), get_arg_n(3), False)
    elif cmd == 'remove':
        project_remove(get_arg_n(2), get_arg_n(3))
    elif cmd == 'update':
        project_update(get_arg_n(2))
    else:
        usage()

if __name__ == "__main__":
    main()