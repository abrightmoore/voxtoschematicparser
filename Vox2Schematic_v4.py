# Read a .vox format file (from MagicaVoxel)
# https://github.com/ephtracy/voxel-model/blob/master/MagicaVoxel-file-format-vox.txt

# 2021-01-04 AB - parser updates for problems encountered with the .vox format having 1 or 4 byte IDs.
#                 consider this a beta release in need of testing, and the parser may need a rewrite later.

import struct
import mcplatform
from os import listdir
from os.path import isfile, join
import glob
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox, MCMaterials

Name2ID = {

    "coarse_dirt" : [3,1],
    "planks_oak" : [5,0],
        "planks_spruce" : [5,1],
        "planks_birch" : [5,2],
        "planks_jungle" : [5,3],

        "planks_big_oak" : [5,5],

    
        "log_spruce" : [17,13],
        "log_jungle" : [17,15],
    
    "sponge" : [19,0],

    
    "lapis_block" : [22,0],

    
    "wool_colored_white" : [35,0],
        "wool_colored_orange" : [35,1],
        "wool_colored_magenta" : [35,2],
        "wool_colored_light_blue" : [35,3],
        "wool_colored_yellow" : [35,4],
        "wool_colored_lime" : [35,5],
        "wool_colored_pink" : [35,6],
        "wool_colored_gray" : [35,7],
        "wool_colored_silver" : [35,8],
        "wool_colored_cyan" : [35,9],
        "wool_colored_purple" : [35,10],
        "wool_colored_blue" : [35,11],
        "wool_colored_brown" : [35,12],
        "wool_colored_green" : [35,13],
        "wool_colored_red" : [35,14],
        "wool_colored_black" : [35,15],
    "gold_block" : [41,0],
    "iron_block" : [42,0],
    
    "stone_slab_top" : [43, 8],
    "sandstone_top" : [43,9],
    "quartz_block_top" : [43,15],

    "obsidian" : [49,0],

    "diamond_block" : [57,0],

    "snow" : [80,0],
    "clay" : [82,0],

    "soul_sand" : [88,0],
    # "stonebrick" : [98,0],
    "mushroom_block_inside" : [99,0],
    "mushroom_block_skin_brown" : [99,14],
    "mushroom_block_skin_stem" : [99,15],
    "mushroom_block_skin_red" : [100,14],
    
    "nether_brick" : [112,0],
    "end_stone" : [121,0],

    "emerald_block" : [133,0],
    "quartz_block_chiseled" : [155,1],
    
    "hardened_clay_stained_white" : [159,0],
        "hardened_clay_stained_orange" : [159,1],
        "hardened_clay_stained_magenta" : [159,2],
        "hardened_clay_stained_light_blue" : [159,3],
        "hardened_clay_stained_yellow" : [159,4],
        "hardened_clay_stained_lime" : [159,5],
        "hardened_clay_stained_pink" : [159,6],
        "hardened_clay_stained_gray" : [159,7],
        "hardened_clay_stained_silver" : [159,8],
        "hardened_clay_stained_cyan" : [159,9],
        "hardened_clay_stained_purple" : [159,10],
        "hardened_clay_stained_blue" : [159,11],
        "hardened_clay_stained_brown" : [159,12],
        "hardened_clay_stained_green" : [159,13],
        "hardened_clay_stained_red" : [159,14],
        "hardened_clay_stained_black" : [159,15],
        
    "log_acacia" : [162,12],
    "log_big_oak" : [162,13],
    
    "prismarine_dark" : [168, 2],
    
    "hardened_clay" : [172,0],
    "coal_block" : [173,0],
    "ice_packed" : [174,0],
    
    "red_sandstone_top" : [181,8]
    
    
    }

GlassColourPallete = [
    (95,  0,  221, 221, 221),
    (95,  1,  219, 125,  62),
    (95,  2,  179,  80, 188),
    (95,  3,  107, 138, 201),
    (95,  4,  177, 166,  39),
    (95,  5,   65, 174,  56),
    (95,  6,  208, 132, 153),
    (95,  7,   64,  64,  64),
    (95,  8,  154, 161, 161),
    (95,  9,   46, 110, 137),
    (95, 10,  126,  61, 181),
    (95, 11,   46,  56, 141),
    (95, 12,   79,  50,  31),
    (95, 13,   53,  70,  27),
    (95, 14,  150,  52,  48),
    (95, 15,   25,  22,  22),
]
    
DefaultColourPallete=[
[105, 99, 89, 162, 12],
[195, 179, 123, 5, 2],
[76, 83, 42, 159, 13],
[119, 85, 59, 3, 1],
[177, 166, 39, 35, 4],
[156, 127, 78, 5, 0],
[103, 77, 46, 5, 1],
[74, 59, 91, 159, 11],
[194, 195, 84, 19, 0],
[221, 221, 221, 35, 0],
[179, 80, 188, 35, 2],
[53, 70, 27, 35, 13],
[231, 228, 220, 155, 1],
[209, 178, 161, 159, 0],
[154, 110, 77, 5, 3],
[38, 67, 137, 22, 0],
[143, 61, 46, 159, 14],
[150, 52, 48, 35, 14],
[45, 28, 12, 17, 13],
[84, 64, 51, 88, 0],
[52, 40, 23, 162, 13],
[219, 219, 219, 42, 0],
[135, 106, 97, 159, 8],
[221, 223, 165, 121, 0],
[186, 133, 35, 159, 4],
[150, 92, 66, 172, 0],
[106, 138, 201, 35, 3],
[87, 67, 26, 17, 15],
[239, 251, 251, 80, 0],
[126, 61, 181, 35, 10],
[113, 108, 137, 159, 3],
[18, 18, 18, 173, 0],
[219, 125, 62, 35, 1],
[81, 217, 117, 133, 0],
[218, 210, 158, 43, 9],
[25, 22, 22, 35, 15],
[161, 83, 37, 159, 1],
[141, 106, 83, 99, 14],
[149, 88, 108, 159, 2],
[37, 22, 16, 159, 15],
[59, 87, 75, 168, 2],
[208, 132, 153, 35, 6],
[64, 64, 64, 35, 7],
[57, 42, 35, 159, 7],
[20, 18, 29, 49, 0],
[65, 174, 56, 35, 5],
[166, 85, 29, 181, 8],
[161, 78, 78, 159, 6],
[77, 51, 35, 159, 12],
[46, 56, 141, 35, 11],
[207, 204, 194, 99, 15],
[118, 70, 86, 159, 10],
[236, 233, 226, 43, 15],
[79, 50, 31, 35, 12],
[182, 37, 36, 100, 14], # 100,14 # 169, 0
[97, 219, 213, 57, 0],
[159, 159, 159, 43, 8],
[44, 22, 26, 112, 0],
[165, 194, 245, 174, 0],
[158, 164, 176, 82, 0],
[202, 171, 120, 99, 0],
[103, 117, 52, 159, 5],
[249, 236, 78, 41, 0],
[46, 110, 137, 35, 9],
[86, 91, 91, 159, 9],
[154, 161, 161, 35, 8],
[61, 39, 18, 5, 5]

]

inputs = (
    ("VOX to Schematic", "label"),
    ("Asset path:", ("string","value=")),
    ("abrightmoore@yahoo.com.au", "label"),
    ("http://brightmoore.net", "label")
    )
    
def closestMaterial(ColourPallete, r, g, b):
    closest = 255*255*3
    best = (1, 0)
    for (mr, mg, mb, bid, dam) in ColourPallete:
        (dr, dg, db) = (r-mr, g-mg, b-mb)
        dist = dr*dr+dg*dg+db*db
        if dist < closest:
            closest = dist
            best = (bid, dam)
    return best

def perform(level, box, options): 
    ASSETPATH = options["Asset path:"]
    FileNames = glob.glob(ASSETPATH+"/*.vox")
    
    for file in FileNames:
        convertVOXFileToSchematic(level, box, file)
    print 'End'
        
def performOLD(level, box, options):
    file = mcplatform.askOpenFile(title="Select the 3D Model", schematics=False) # After @GentleGiantJGC
    if file == None:
        raise Exception('No Model File Specified')
    print 'Start '+file
    (version,numModels,VOXchunks,matdefs,matlist) = parseVOXFile(file)
    colours= getRGBA(VOXchunks)
    renderModels(level,box,VOXchunks,matdefs,matlist,colours)
    
    print 'End'

def convertVOXFileToSchematic(level, box, file):
    print 'Convert '+file
    (version,numModels,VOXchunks,matdefs,matlist) = parseVOXFile(file)
    colours = getRGBA(VOXchunks)
    (w,h,d) = getSize(VOXchunks)
    print w,h,d
    schem = MCSchematic((w,d,h))
    box1 = BoundingBox((0,0,0),(w,d,h))
    renderModels(schem,box1,VOXchunks,matdefs,matlist,colours)
    schem.saveToFile(file+".schematic")
    
    print 'Converted '+file

def getSize(chunks):
    RGBA = []
    maxX = 0
    maxY = 0
    maxZ = 0
    for (type,data) in chunks:
        if type == "SIZE":
            (x,y,z) = data
            if x > maxX:
                maxX = x
            if y > maxY:
                maxY = y
            if z > maxZ:
                maxZ = z
    return (maxX,maxY,maxZ)
                
    
def getRGBA(chunks):
    RGBA = []
    for (type,data) in chunks:
        if type == "RGBA":
            return data
            
    for (r, g, b, id, data) in DefaultColourPallete:
        RGBA.append((r,g,b,255))
    return RGBA # Default if no RGBA chunk found
        
def renderModels(level,box,chunks,matdefs,matlist,colours):
    MATERIAL = (1,0)
    print colours
    for (type,data) in chunks:
        print type
        if type == "XYZI":
            for (x,y,z,i) in data:
                if i in matlist:
                    # Check matdefs
                    (r,g,b,a) = colours[(i-1)%len(colours)]
                    (block, damage) = closestMaterial(DefaultColourPallete, r,g,b)
                    type = "Block"
                    for (mat_id,mat_type,mat_weight,mat_prop,mat_prop_plastic,  mat_prop_roughness, mat_prop_specular, mat_prop_ior,mat_prop_attenuation, mat_prop_power, mat_prop_glow) in matdefs: # Check if this is a special material
                        #print i,mat_id,mat_type,mat_weight,mat_prop,mat_prop_plastic,  mat_prop_roughness, mat_prop_specular, mat_prop_ior,mat_prop_attenuation, mat_prop_power, mat_prop_glow
                        if i == mat_id:
                            if mat_type == 2: # This is Glass
                                (block, damage) = closestMaterial(GlassColourPallete, r,g,b)
                    level.setBlockAt(box.maxx-1-x, box.miny+z, box.minz+y, block)
                    level.setBlockDataAt(box.maxx-1-x, box.miny+z, box.minz+y, damage)  
    
def parseVOXChunk(f):
    print "Current file position "+str(f.tell())
    #Chunk ID
    bytes = f.read(4)
    # print "4 bytes:", bytes
    chunk_id = struct.unpack(">4s",  bytes)
    print "Chunk ID "+str(chunk_id[0])
    
    # Num bytes of chunk content
    bytes = f.read(4)
    if len(bytes) == 4:
        numBytesChunkContent = struct.unpack('<I', bytes)
    elif len(bytes) == 1:
        numBytesChunkContent = struct.unpack('<B', bytes)
    else:
        numBytesChunkContent = 0
    # Num bytes of children chunks
    bytes = f.read(4)
    print "AB ", bytes, len(bytes)
    if len(bytes) == 4:
        numBytesChildrenChunks = struct.unpack('<I', bytes)
    elif len(bytes) == 1:
        numBytesChildrenChunks = struct.unpack('<B', bytes)
    else:
        numBytesChildrenChunks = 0
        
    if type(numBytesChunkContent) == list:
        if len(numBytesChunkContent) > 0:
            print "Chunk Content "+str(numBytesChunkContent[0])
    if type(numBytesChildrenChunks) == list:
        if len(numBytesChildrenChunks) > 0:
            print "Children Chunks "+str(numBytesChildrenChunks[0])
    return (chunk_id,numBytesChunkContent,numBytesChildrenChunks)
    
    
def parseVOXFile(filename): # After @matesteinforth import_vox.py
    chunks = []
    matlist = []
    matdefs = []
    version = -1
    numModels = -1
    sizeX = -1
    sizeY = -1
    sizeZ = -1
    
    with open(filename, 'rb') as f:
        #check filetype
        bytes = f.read(4)
        file_id = struct.unpack(">4s",  bytes)
        if file_id[0] == 'VOX ':
            #header
            bytes = f.read(4) 
            version = struct.unpack('<I', bytes)
            (chunk_id,MainChunkContent,MainChildrenChunksBytes) = parseVOXChunk(f) 
            fileStartPos = f.tell()
            fileEndPos = fileStartPos + MainChunkContent[0] + MainChildrenChunksBytes[0]
            print "File - "+str(fileStartPos)+" "+str(fileEndPos)
            if chunk_id[0] == 'MAIN': # Special top level container chunk with no contents
                if MainChunkContent[0] != 0:
                    raise Exception('Unexpected content in MAIN chunk. Has the specification changed?\nhttps://github.com/ephtracy/voxel-model/blob/master/MagicaVoxel-file-format-vox.txt')
                while f.tell() < fileEndPos: # Parse all child chunk content
                    (chunk_id,numBytesChunkContent,numBytesChildrenChunks) = parseVOXChunk(f) 

                    if chunk_id[0] == 'PACK':
                        bytes = f.read(4) 
                        numModels = struct.unpack('<I', bytes)
                    elif chunk_id[0] == 'SIZE':
                        bytes = f.read(4) 
                        sizeX = struct.unpack('<I', bytes)                      
                        bytes = f.read(4) 
                        sizeY = struct.unpack('<I', bytes)  
                        bytes = f.read(4) 
                        sizeZ = struct.unpack('<I', bytes)
                        print (sizeX,sizeY,sizeZ)
                        chunks.append((chunk_id[0],(sizeX[0],sizeY[0],sizeZ[0])))
                    elif chunk_id[0] == 'XYZI':
                        #read number of voxels, stuct.unpack parses binary data to variables
                        bytes = f.read(4)
                        numvoxels = struct.unpack('<I', bytes)
                        print 'numvoxels '+str(numvoxels)
                        voxels = []
                        for x in range(0, numvoxels[0]):               
                            #read voxels, ( each voxel : 1 byte x 4 : x, y, z, colorIndex ) x numVoxels
                            bytes = f.read(4)
                            voxel = struct.unpack('<bbbB', bytes)
                            voxels.append(voxel)
                            #update material list, generate new material only if it isn't in the list yet
                            matid = voxel[3]
                            if matid not in matlist:
                                matlist.append(matid)
                        chunks.append((chunk_id[0],voxels))
                    elif chunk_id[0] == 'RGBA':
                        RGBAs = []
                        for i in xrange(0,256):
                            bytes = f.read(4)
                            RGBA = struct.unpack('<BBBB', bytes)
                            RGBAs.append(RGBA)
                        chunks.append((chunk_id[0],RGBAs))
                    elif chunk_id[0] == 'MATT':
                        curpos = f.tell()
                        while f.tell() < curpos + numBytesChunkContent[0]:
                            bytes = f.read(4)
                            mat_id = struct.unpack('<I', bytes)
                            bytes = f.read(4)
                            mat_type = struct.unpack('<I', bytes)
                            bytes = f.read(4)
                            mat_weight = struct.unpack('<f', bytes)
                            bytes = f.read(4)
                            mat_prop = struct.unpack('<I', bytes)
                            
                            mat_prop_plastic = [0]
                            mat_prop_roughness = [0]
                            mat_prop_specular = [0]
                            mat_prop_ior = [0]
                            mat_prop_attenuation = [0]
                            mat_prop_power = [0]
                            mat_prop_glow = [0]
                            
                            
                        #   print mat_id,mat_type,mat_weight,mat_prop
                            if (mat_prop[0] & 0x01) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_plastic = struct.unpack('<f', bytes)
                            if (mat_prop[0] & 0x02) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_roughness = struct.unpack('<f', bytes)
                            if (mat_prop[0] & 0x04) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_specular = struct.unpack('<f', bytes)
                            if (mat_prop[0] & 0x08) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_ior = struct.unpack('<f', bytes)
                            if (mat_prop[0] & 0x10) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_attenuation = struct.unpack('<f', bytes)
                            if (mat_prop[0] & 0x20) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_power = struct.unpack('<f', bytes)
                            if (mat_prop[0] & 0x40) != 0: # Bit test
                                bytes = f.read(4)
                                mat_prop_glow = struct.unpack('<f', bytes)
                            
                        #   print mat_prop_plastic, mat_prop_roughness, mat_prop_specular, mat_prop_ior,mat_prop_attenuation, mat_prop_power, mat_prop_glow
                        
                        matdefs.append((mat_id[0],mat_type[0],mat_weight[0],mat_prop[0],mat_prop_plastic[0],    mat_prop_roughness[0], mat_prop_specular[0], mat_prop_ior[0],mat_prop_attenuation[0], mat_prop_power[0], mat_prop_glow[0]))
                    else:
                        print "Unknown chunk ID: ignored"
                        # f.seek(numBytesChunkContent[0],1) # Skip
#   print "version "+str(version)
#   print "numModels "+str(numModels)
#   print chunks
#   print matlist
    return (version,numModels,chunks,matdefs,matlist)