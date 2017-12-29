File Tag Utility (ftag)
=======================

Utility to tag files with group names


Notes
-----

 - Always determien the root DB folder from file being written to
 - Everything with no tags assigned gets notag
 - Psuedo tag with file, folder, link, and device?
 - Move and copy bring existing tags as well 
 - Ignore owners, groups, and permissions
 - Allow tagging of directories too
 

Example Usages
--------------

    ptag init .

    ptag tag +drupal_base *
    ptag tag -drupal_base sites/default/files
    ptag tag +panels sites/default/modules/panels
    ptag tag -drupal_base . --if panels
    
    ptag copy ~/src/ref-1.2.3/* sites/default/modules --tag new
    ptag cp -rv --tag new ~/src/ref-1.2.3/* sites/default/modules
    ptag mv -v --tag new ~/src/ref-1.2.3/* sites/default/modules
    ptag mv sites/default/modules/ref sites/all/modules/ref
    
    ptag find / --if notag
    ptag find ./ --if drupal_base --abs
    
    ptag clean (/root/folder)
    
    ptag ls * -1
    
    ptag exec -c 'rm {}' --if drupal_base
    

Query
-----
    
file,folder = has a file or folder tag

file+folder = has both file and folder tags

file+~notag = has file tag, but not the notag tag
    
    
Auto Tags
---------

 - notag: No usre tag assigned
 - file: A file object
 - folder: A folder object
 
 
