import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
import math as m
# Cria janela de interface do windows
root = tk.Tk()
root.withdraw()
root.title('GCODE Reader')

# A janela contém um seletor de arquivos cujo output é o caminho de um arquivo
file_path = filedialog.askopenfilename(filetypes=[('Text Files', '*.MPF')])

# Separa strings do caminho e da extensão do arquivo e cria um novo arquivo com mesmo nome e extensão acrescido de sufixo
root, ext = os.path.splitext(file_path)
new_root = root + '_corrigido'
new_file_path = new_root + ext

# Read the contents of the selected file into a string variable
with open(file_path, 'r') as f:
    gcode = f.readlines()
    
# Função de busca e correção de trechos com não conformidade
def main(gcode_file):
    
    gcode = gcode_file
    for i in range(len(gcode)):
        if 'R507=2' in gcode[i] or 'R507=3' in gcode[i]: #checa se o tubo é quadrado ou retangular
            rectang_TubeMod(gcode)
         
            break
        if 'R507=1' in gcode[i]: #checa se o tubo é redondo
            round_TubeMod(gcode)
          
            break
        
def rectang_TubeMod(gcode_file):  
    i = 0
    gcode = gcode_file
    lastX = 0
    lastY = 0
    lastA = 0
    linearFeed = True
    angularFeed = False
 
    while i < len(gcode):
        
        if 'F=R529' in gcode[i]:
            angularFeed = True #Angular motion
            linearFeed = False 
        if 'F=R47' in gcode[i] or 'FGROUP(X1,Y1)' in gcode [i]:
            angularFeed = False #Linear motion
            linearFeed = True 
        if 'R502' and 'R503' in gcode[i]:
            tubeWidth = float(gcode[i].split('02=')[1].split(' ')[0])
            tubeHeight = float(gcode[i].split('03=')[1].split(' ')[0])
            
        if gcode[i].startswith('G0'):
            
            X1,Y1,A1,lastX,lastY,lastA = saveCoordinates(gcode,i,lastX,lastY,lastA)
       
            for j in range(i+1, len(gcode)):

                if 'F=R529' in gcode[j]:
                    angularFeed = True #Angular motion
                    linearFeed = False
                if 'F=R47' in gcode[j] or 'FGROUP(X1,Y1)' in gcode[j]:
                    angularFeed = False #Linear motion
                    linearFeed = True 
                if gcode[j].startswith('G0'):
                    
                    X2,Y2,A2,lastX,lastY,lastA = saveCoordinates(gcode,j,lastX,lastY,lastA)
                    
                    angularMove,linearMove = movimentVerifierRectang(X1,X2,Y1,Y2,A1,A2)
                    
                   
                        
                    if gcode[j].startswith('G00'):
                        i = j-1
                        break

                    if linearMove is True and linearFeed is True:
                        i = j-1
                        break

                    if linearMove is True and linearFeed is False:
                        
                        gcode.insert(j,'F=R47\n')
                        gcode.insert(j+1,'G64\n')
                        linearFeed = True
                        angularFeed = False
                        i = j+1
                        

                    if angularMove is True and angularFeed is True:
                        i = j-1
                        break
                    
                    if angularMove is True and angularFeed is False:
                        
                        gcode.insert(j,'FGROUP(X1,Y1,A)\n')
                        gcode.insert(j+1,'G645\n')
                        gcode.insert(j+2,'F=R529*360\n')
                        linearFeed = False
                        angularFeed = True
                        i = j+2
                        break
        i = i+1
    #Escrevendo código G corrigido no novo arquivo criado anteriormente       
    with open(new_file_path, 'w') as f:
        for i in gcode:
            f.write(i)  
               
def round_TubeMod(gcode_file): 
    i = 0
    gcode = gcode_file
    lastX = 0
    lastY = 0
    lastA = 0
    linearFeed = True
    angularFeed = False
    
    while i < len(gcode):
        
        if 'F=R529' in gcode[i]:
            angularFeed = True #Angular motion
            linearFeed = False 
        if 'F=R47' in gcode[i] or 'FGROUP(X1,Y1)' in gcode [i]:
            angularFeed = False #Linear motion
            linearFeed = True 
        if 'R504' in gcode[i]:
            tubeRadius = float(gcode[i].split('04=')[1].split(';')[0])
            print('raio do tubo = ', tubeRadius)
            
        if gcode[i].startswith('G0'):
            
            X1,Y1,A1,lastX,lastY,lastA = saveCoordinates(gcode,i,lastX,lastY,lastA)
            
            for j in range(i+1, len(gcode)):

                if 'F=R529' in gcode[j]:
                    angularFeed = True #Angular motion
                    linearFeed = False
                if 'F=R47' in gcode[j] or 'FGROUP(X1,Y1)' in gcode[j]:
                    angularFeed = False #Linear motion
                    linearFeed = True 
                if gcode[j].startswith('G0'):
                    
                    X2,Y2,A2,lastX,lastY,lastA = saveCoordinates(gcode,j,lastX,lastY,lastA)
                    
                    angularMove,linearMove,ratioXA,dX,dA = movimentVerifierRound(X1,X2,Y1,Y2,A1,A2,tubeRadius)
                    
                   
                        
                    if gcode[j].startswith('G00'):
                        i = j-1
                        break

                    if linearMove is True and linearFeed is True:
                        i = j-1
                        break

                    if linearMove is True and linearFeed is False:
                        print('angulo de corte projetado = ', ratioXA)
                        print('F=R47 inserido na linha ', j, '')
                        gcode.insert(j,'F=R47\n')
                        gcode.insert(j+1,'G64\n')
                        linearFeed = True
                        angularFeed = False
                        i = j+1
                        

                    if angularMove is True and angularFeed is True:
                        i = j-1
                        break
                    
                    if angularMove is True and angularFeed is False:
                        print('angulo de corte projetado = ', ratioXA)
                        print('F=R529*360 inserido na linha ', j)
                        gcode.insert(j,'FGROUP(X1,Y1,A)\n')
                        gcode.insert(j+1,'G645\n')
                        gcode.insert(j+2,'F=R529*360\n')
                        linearFeed = False
                        angularFeed = True
                        i = j+2
                        break
        i = i+1
    #Escrevendo código G corrigido no novo arquivo criado anteriormente       
    with open(new_file_path, 'w') as f:
        for i in gcode:
            f.write(i)
            
                            
def saveCoordinates(gcode_file,line,lastX,lastY,lastA):
    i = line
    gcode = gcode_file
    if 'X' in gcode[i]:
        X = float(gcode[i].split('X')[1].split()[0])
        lastX = float(gcode[i].split('X')[1].split()[0])
        
    else:
        X = lastX
    
    if 'Y' in gcode[i]:
        Y = float(gcode[i].split('Y')[1].split()[0])
        lastY = float(gcode[i].split('Y')[1].split()[0])
    else:
        Y = lastY

    if 'A' in gcode[i]:
        A = float(gcode[i].split('A')[1].split()[0])
        lastA = float(gcode[i].split('A')[1].split()[0])
        
    else:
        A = lastA
    return X, Y, A, lastX, lastY, lastA

def movimentVerifierRound(X1,X2,Y1,Y2,A1,A2,tubeRadius):
    dX = abs(X1 - X2)
    dY = abs(Y1 - Y2)
    dA = abs(A1 - A2)
    
    if dX == 0 and dA != 0:
       linearMove = False
       angularMove = True
       ratioXA = 90
    if dX == 0 and dA == 0:
        linearMove = True
        angularMove = False
        ratioXA = 90
    if dX != 0:
        #ratioXA = dX/dA
        dA_ = m.radians(dA)
        dY_ = tubeRadius*dA_
        ratioXA = m.degrees(m.atan(dY_/dX))
        #print('angulo da reta = ',ratioXA)
        if ratioXA <= 10:
                
            linearMove = True
            angularMove = False
        else:
            angularMove = True
            linearMove = False

    return angularMove,linearMove,ratioXA,dX,dA

def movimentVerifierRectang(X1,X2,Y1,Y2,A1,A2):
    dX = abs(X1 - X2)
    dY = abs(Y1 - Y2)
    dA = abs(A1 - A2)
    
    
 
    if dA == 0:
        linearMove = True
        angularMove = False
        ratioYA = 1000000
    if dA != 0:
        ratioYA = dY/dA
        
        if ratioYA >= 15:
                
            linearMove = True
            angularMove = False
        else:
            angularMove = True
            linearMove = False

    return angularMove,linearMove
if __name__ == "__main__":
    main(gcode)