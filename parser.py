from constants import ModelData

def parse_obj(path: str):
    with open(path) as file:
        file_data = file.readlines()
    
    vertices = []
    faces = []
    
    for line in file_data:
        line = line.strip()
        
        line_data = line.split()
        
        s_data = None
        
        if line.startswith("v "):
            _, x, y, z = line_data
            
            vertices.append((float(x), float(y), float(z)))
        elif line.startswith("f "):
            line_data.pop(0)
            
            s_data = []
            
            for coord in line_data:
                u_f_data = coord.split("/")
                
                f_fin_data = None
                
                # Face index
                if len(u_f_data) == 1:
                    f_data = int(u_f_data[0]) - 1
                    
                    f_fin_data = f_data
                # Face index + Texture index
                elif len(u_f_data) == 2:
                    f_data, t_data = u_f_data
                    f_data = int(f_data) - 1
                    
                    f_fin_data = f_data # TODO  Implement textures
                # Face index + Texture index + Normal vector
                elif len(u_f_data) == 3:
                    f_data, t_data, vn_data = u_f_data
                    f_data = int(f_data) - 1
                    
                    f_fin_data = f_data # TODO  Implement vector normals
                
                if f_fin_data is not None:
                    s_data.append(f_fin_data)
            
            faces.append(s_data)
        else:
            pass
    
    return ModelData(v = vertices, f = faces)
            
            
            

