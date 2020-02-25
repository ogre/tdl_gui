import os, string, sys
import re

#MariTemplate = r'(.+)([0-9]{4})(\.{1}.+)'
MariTemplate = r'(.+)([0-9]{4})(.+)' # this template does not require .dot after patch
MudBoxTemplate = r'(.+)(_u)([0-9]+)(_v)([0-9]+)(\.{1}.+)'

# find 4-digit patch number starting from end
def GetMariTemplate(i_file):
    template = MariTemplate
    searchObj = re.search( template, i_file)
    elements = searchObj.groups()
    
    result = ( string.join(elements[:-2]), elements[-2], elements[-1] )
    return result

# get relative file names (no full paths), returns matching patches
def FilterMariPatches(i_file, fileList):
    (base, patch, ext) = GetMariTemplate( i_file )
    
    patch_template = ""
    patch_template += string.replace(base, ".", "\\.") # escape '.'
    patch_template += r'([0-9]{4})' 
    patch_template += string.replace(ext, ".", "\\.") # escape '.'
    patch_template += r'$' # end of line
    
    return filter(lambda x: re.match(patch_template, x), fileList)


# find 2 patch numbers _u _v
def GetMudboxTemplate(i_file):
    template = MudBoxTemplate
    searchObj = re.search( template, i_file)
    elements = searchObj.groups()    
    
    result = ( string.join(elements[:-5]), elements[-4], elements[-2], elements[-1] ) # base %d %d ext
    return result

# get relative file names (no full paths), returns matching patches
def FilterMudboxPatches(i_file, fileList):
    (base, patch_u, patch_v, ext) = GetMudboxTemplate( i_file )
    print (base, patch_u, patch_v, ext)
    
    patch_template = ""
    patch_template += string.replace(base, ".", "\\.") # escape '.'
    patch_template += '_u'
    patch_template += r'([0-9]+)' 
    patch_template += '_v'
    patch_template += r'([0-9]+)' 
    patch_template += string.replace(ext, ".", "\\.") # escape '.'
    patch_template += r'$' # end of line
    
    return filter(lambda x: re.match(patch_template, x), fileList)

def IsMariPatch(i_file):
    return (re.match(MariTemplate, i_file) != None)

def IsMudboxPatch(i_file):
    return (re.match(MudBoxTemplate, i_file) != None)

if __name__ == '__main__':
    
    files = os.listdir(".")
    
    #print FilterMudboxPatches("dfsd_u1_v1.jpg", files)
    #print FilterMudboxPatches("dfsd_u1_v1.jpg.tdl", files)
    
    '''
    print IsMariPatch("dfsd.1001.jpg")
    print IsMariPatch("dfsd_1001.jpg")
    print IsMariPatch("dfsd.1001.jpg.tdl")
    print IsMariPatch("dfsd_1001.jpg.tdl")
    print IsMariPatch("tex_v0005.0052.1001.jpg")
    print IsMariPatch("dfsd_u1_v1.jpg")
    print IsMariPatch("dfsd_u1_v1.jpg.tdl")
    
    print "****************"
    
    print IsMudboxPatch("dfsd.1001.jpg")
    print IsMudboxPatch("dfsd_1001.jpg")
    print IsMudboxPatch("dfsd.1001.jpg.tdl")
    print IsMudboxPatch("dfsd_1001.jpg.tdl")
    print IsMudboxPatch("tex_v0005.0052.1001.jpg")
    print IsMudboxPatch("dfsd_u1_v1.jpg")
    print IsMudboxPatch("dfsd_u1_v1.jpg.tdl")
    '''
    
    '''
    files = os.listdir(".")
    print FilterMariPatches("dfsd.1001.jpg", files)
    print FilterMariPatches("dfsd_1001.jpg", files)
    print FilterMariPatches("dfsd.1001.jpg.tdl", files)
    print FilterMariPatches("dfsd_1001.jpg.tdl", files)
    print FilterMariPatches("tex_v0005.0052.1001.jpg", files)
    '''
    
    files = os.listdir(".")
    
    print IsMudboxPatch("dfsd_u4_v2.jpg")
    print FilterMudboxPatches("dfsd_u4_v2.jpg", files)
    
    
    '''
    GetMariTemplate("tekstura.1023.exr")
    GetMariTemplate("tekstura.1023.exr.tdl")
    GetMariTemplate("tekstura_1023.exr")
    GetMariTemplate("tekstura_1023.exr.tdl")
    
    GetMariTemplate("tekstura_v5.0005.1023.exr")
    GetMariTemplate("tekstura_v5.0005.1023.exr.tdl")
    '''
    