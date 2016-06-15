import os
import sys
import argparse
import json
import glob
import fnmatch
import shutil
import datetime as dt
import slimit
import csscompressor

from lxml import etree, html
from lxml.html import builder as E


class MergeObject():

    def __init__(self, into):
        self.into = into
        self.merging_files = []
        self.added = False


def get_parser():
    parser = argparse.ArgumentParser(usage="python html_builder.py [-c config_file] index.html",
                                     description="Python HTML Project Builder")
    parser.add_argument("-c", dest="config_file", help="builder config file.")
    parser.add_argument("--input", "-i", dest="input_file_i",
                        help="html input file to process.")
    parser.add_argument("input_file", nargs="*",
                        help="html input file to process.")

    return parser


def main():
    # Get and parse command-line arguments:
    parser = get_parser()
    args = parser.parse_args()
    # print(args)

    input_file = args.input_file[0] if args.input_file else args.input_file_i
    if not input_file:
        print("Please provide an html file as input file.")
        parser.print_help()
        sys.exit(1)

    config_file = args.config_file
    if not config_file:
        config_file = os.path.abspath(os.path.join(os.path.dirname(input_file), "builder_config.json"))
    
    if not os.path.exists(config_file):
        print("Please provide a builder config file.")
        parser.print_help()
        sys.exit(1)
    
    configs = json.load(open(config_file, encoding="utf-8"))
    configs["file"] = os.path.basename(config_file)
    # print(configs)

    configs["minify"] = [configs["minify"]]
    if "all" in configs["minify"]:
        configs["minify"].extend(["js", "css"])

    if configs["timeStamp"]:
        configs["timeStamp"] = "_{0:%Y}-{0:%m}-{0:%d}_{1}" \
                                .format(dt.datetime.now(), str(dt.datetime.now().timestamp())[:-7])
    else:
        configs["timeStamp"] = ""

    # Start building process:
    build(input_file, configs)


def build(input_file, configs):
    # Making build folder
    build_name = os.path.normpath(configs["buildPath"] + configs["timeStamp"])
    base_dir = os.path.abspath(os.path.dirname(input_file))
    build_dir = os.path.join(base_dir, build_name)
    os.makedirs(build_dir, exist_ok=True)

    # Getting list of excluded files:
    excludes = get_files(base_dir, configs["exclude"])
    
    # Merging requested files in config-file:
    merged_objects = merge(configs["merge"], base_dir, build_dir, excludes, configs["obfuscate"])
    merged_files = [f for mo in merged_objects for f in mo.merging_files]

    # Traverse directory of the given html file recursively and process unmerged remaining files:
    for root, dirs, files in os.walk(base_dir):

        if build_name in dirs:
            dirs.remove(build_name)

        if files:
            # remove config file from files list:
            if configs["file"] in files:
                files.remove(configs["file"])

        dest = os.path.join(build_dir, os.path.relpath(root, base_dir))
        for file in files:
            file_path = os.path.join(root, file)
            # If file was already part of a merge process:
            if file_path in merged_files or file_path in excludes:
                continue

            if is_min_file_exists(file, file_path):
                continue

            os.makedirs(dest, exist_ok=True)

            ext = os.path.splitext(file)[1][1:]
            if ext in configs["minify"] and not is_min_file(file):
                # Processing(minifying) js/css file:
                print("minifying %s" % file_path)
                min_file_path = os.path.join(dest, os.path.splitext(os.path.basename(file))[0] + ".min." + ext)
                if ext == "js":
                    data = slimit.minify(open(file_path, "r", encoding="utf-8").read(), mangle=configs["obfuscate"], mangle_toplevel=False)
                else:
                    data = csscompressor.compress(open(file_path, "r", encoding="utf-8").read())
                
                with open(min_file_path, "w", encoding="utf-8") as min_file:
                    min_file.write(data)

            else:
                # just copy the file.
                print("copying %s" % file_path)
                shutil.copy2(file_path, dest)


    # Now editing given html file <script> and <link> tags:
    print("Updating html file...")
    tree = None
    with open(os.path.join(build_dir, os.path.basename(input_file)), "r", encoding="utf-8") as html_file:
        tree = html.parse(html_file)

        # Updating javascript tags:
        for tag in tree.findall("//script[@src]"):
            if tag.attrib["src"].startswith("http"):
                continue
            # Get the complete path of source file:
            src_file = os.path.normpath(os.path.join(base_dir, tag.attrib["src"]))
            if src_file in merged_files:
                # Source file is part of a merge:
                mo = get_merge_object(merged_objects, src_file)
                if mo is not None and not mo.added:
                    # Replacing new merged file tag with old one:
                    new_tag = E.SCRIPT(type="text/javascript", src=mo.into)
                    tag.getparent().replace(tag, new_tag)
                    mo.added = True
                else:
                    # Merged file tag was already added.
                    tag.getparent().remove(tag)
            elif not src_file.endswith(".min.js"):
                # replacing source file with minified one:
                tag.attrib["src"] = os.path.relpath(src_file, base_dir)[:-2] + "min.js"

        # Updating stylesheet link tags:
        for tag in tree.xpath('//*[@rel="stylesheet" or @media="all" or @media="screen"]'):
            if tag.attrib["href"].startswith("http"):
                continue
            # Get the complete path of source file:
            href_file = os.path.normpath(os.path.join(base_dir, tag.attrib["href"]))
            if href_file in merged_files:
                # Source file is part of a merge:
                mo = get_merge_object(merged_objects, href_file)
                if mo is not None and not mo.added:
                    # Replacing new merged file tag with old one:
                    new_tag = E.LINK(rel="stylesheet", type="text/css", href=mo.into)
                    tag.getparent().replace(tag, new_tag)
                    mo.added = True
                else:
                    # Merged file tag was already added.
                    tag.getparent().remove(tag)
            elif not href_file.endswith(".min.css"):
                # replacing href file with minified one:
                tag.attrib["href"] = os.path.relpath(href_file, base_dir)[:-3] + "min.css"

    with open(os.path.join(build_dir, os.path.basename(input_file)), "wb") as html_file:
        html_file.write(html.tostring(tree, encoding="utf-8", pretty_print=True))

    print("Done!")


def merge(merge_info, base_dir, build_dir, excludes, obfuscate=False):
    """For merging files there are three cases to consider:
        1. path ends with one star(*)
        2. path ends with two star(**)
        3. a file path
    """
    merged_objects = []

    for dest_path in merge_info.keys():
        print("start merging files into: %s..." % dest_path)
        merging_files = []
        ext = ""
        if dest_path.endswith("js"):
            ext = "js"
        elif dest_path.endswith("css"):
            ext = "css"

        merging_files = get_files(base_dir, merge_info[dest_path], ext)

        # Now open, minify and merge files:
        os.makedirs(os.path.join(build_dir, os.path.dirname(dest_path)), exist_ok=True)
        dest_file = open(os.path.join(build_dir, dest_path), "w", encoding="utf-8")

        for f in merging_files:
            if f in excludes:
                continue

            print("    processing file:", f)
            if is_min_file(f):
                print("    already minified:", f)
                data = open(f, "r", encoding="utf-8").read()
            elif ext == "js":
                data = slimit.minify(open(f, "r", encoding="utf-8").read(), mangle=obfuscate, mangle_toplevel=False)
            elif ext == "css":
                data = csscompressor.compress(open(f, "r", encoding="utf-8").read())

            dest_file.write(data)
        dest_file.close()
        print("finish merging %s files into %s" % (len(merging_files), dest_path))
        
        # Creating merge-object. we use this later to keep order of script/css tags:
        mo = MergeObject(dest_path)
        mo.merging_files = merging_files
        merged_objects.append(mo)
    # End of merge_info loop

    return merged_objects


def get_merge_object(objects, file):
    for mo in objects:
        if file in mo.merging_files:
            return mo
    return None


def get_files(base_dir, paths, ext="*"):
    # Return list of files paths: dir/* means all files in dir, dir/** means all files in dir and all subdirs.
    results = []
    for p in paths:
        p = os.path.join(base_dir, p)
        if p[-2:].count("*") == 1:
            # Getting all files in specifiec folder:
            # print(p, glob.glob(p + "/*.%s" % (p, ext)))
            results.extend([ os.path.join(p[:-1], f) for f in glob.glob("%s/*.%s" % (p[:-1], ext)) ])
        
        elif p[-2:].count("*") == 2:
            # Getting all files in specified folder recursively:
            for root, dirs, files in os.walk(p[:-2]):
                results.extend([ os.path.join(root, f) for f in fnmatch.filter(files, "*." + ext) ])

        else:
            results.append(p)

    return results


def is_min_file(fname):
    return (".min.js" in fname or ".min.css" in fname)

def is_min_file_exists(file, path):
    dir = os.path.dirname(path)
    namext = os.path.splitext(file)
    min_file = os.path.join(dir, namext[0] + ".min" + namext[1])

    return os.path.exists(min_file)




if __name__ == "__main__":
    main()
