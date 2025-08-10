import os
import time
macrotarget = r'C:\Users\Utente\Desktop\cartesian\test'
orcapath = r'C:\\Users\\Utente\\Documents\\Downloads\\orca'
qmtxt= os.path.join(macrotarget,'qm.out')

yasarapath= r'C:\yasara'
simulation_time=input('simulation time (fs):' )

def remove_blank_lines(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    with open(output_file, 'w') as file:
        for line in lines:
            if line.strip():  # check if the line is not empty
                file.write(line)

def merge_files(file1_path, file2_path, merged_output_file_path):
    # Read the contents of the first file
    with open(file1_path, 'r') as f1:
        data1 = f1.readlines()

    # Read the contents of the second file
    with open(file2_path, 'r') as f2:
        data2 = f2.readlines()

    # Ensure both files have the same number of lines
    if len(data1) != len(data2):
        raise ValueError("Files do not have the same number of lines")

    # Merge the contents column-wise
    merged_data = []
    for line1, line2 in zip(data1, data2):
        merged_line = f"{line1.strip()} {line2.strip()}\n"
        merged_data.append(merged_line)

    # Write the merged data to a new file
    with open(merged_output_file_path, 'w+') as outfile:
        outfile.writelines(merged_data)

 

def delete_lines_from_file(file_path, line_numbers):
    # Read all lines from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Remove the lines at the specified indices
    # Note: line_numbers are 1-based, convert to 0-based
    remaining_lines = [line for idx, line in enumerate(lines) if idx + 1 not in line_numbers]

    # Write the remaining lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(remaining_lines)







def loadstrcture(yasarapath, macrotarget,orcapath):
   content= '''
Showmessage 'Load your structure'
wait continuebutton
numeroobj= CountObj all
if numeroobj >0
  Showmessage 'Select your QM atoms'
  wait continuebutton
  SaveSce (MACROTARGET)/MM.sce
  atomlist()= ListAtom Selected
  MakeTab atomlistqm,Dimensions=1
  numero= Countatom selected
  Tabulate (atomlist)
  SaveTab atomlistqm,(MACROTARGET)/atom.txt,Format=Text,Columns=1,NumFormat=6.0f,atom_numero
  DelTab all
  MakeTab MyTable,Dimensions=1
  for n in atomlist()
    #bfactoratom (n),(n)
    propatom (n),(n)
  Delatom !selected
  #wait continuebutton
  AddHydObj 1
  ForceField AMBER14,SetPar=yes
  Interactions Bond,Angle,Dihedral,Planarity,Coulomb,VdW
  #wait continuebutton
  refresh_numero()= ListAtom Selected 
  SaveXYZ selected, '(MACROTARGET)/QM.xyz'
  UnSelectAll
  charge= Chargeobj 1
  for i in refresh_numero()
    p=propatom (i)
    p= (00+p)
    if p == 0      
      Tabulate (00+i)
      Tabulate (00+charge)
      
      SelectAtom (i), Mode=Add #p=refresh_numero
    else
      print ('ok')#p= (00+p) 
  

SaveTab MyTable,(MACROTARGET)/newadded.txt,Format=Text,Columns=2,NumFormat=6.0f,newly_added_Atom Charge_all
DelTab all
exit 
  
'''
   macrofile= os.path.join(macrotarget,'qm.mcr')
   atominfo= os.path.join(macrotarget,'atom.txt')
   f= open(macrofile,'w')
   f.write(str("MACROTARGET = '"+macrotarget+"'\n"))
   f.write(str(content))
   f.close()
   yasara= os.path.join(yasarapath,'YASARA.exe')
   os.system(yasara+' '+macrofile)
   orca= os.path.join(orcapath,'orca')
   os.chdir(macrotarget)
   input_file = os.path.join(macrotarget, 'newadded.txt')
   output_file = os.path.join(macrotarget, 'newadded.txt')
   remove_blank_lines(input_file, output_file)
   with open(output_file, 'r') as file:
    # Read all lines
       lines = file.readlines()

 # Get the number of lines except the first line (header)
   line_count = len(lines) - 1
   second_column_first_value = lines[1].split()[1]
   charge_info = str(second_column_first_value)
   qminp= os.path.join(macrotarget,'QM.inp')
   qmout= os.path.join(macrotarget,'QM.out')
   qmxyz= os.path.join(macrotarget,'QM.xyz')
   f= open(qmxyz,'r')
   data=f.readlines()
   data=''.join(data[2:])
   #print(data)
   orcainp= open(qminp,'w+')
   orcainp.write('!SP PM3 RHF ')
   orcainp.write('\n\n* xyz  '+str(charge_info)+' 1 \n')
   orcainp.write(data+'*\n')
   orcainp.close()
   #os.chdir(yasarapath)
   #os.chdir(macrotarget)
   #time.sleep(5)
   print('QM single point optimization is in process for QM atoms..')
   os.system(orca+' '+qminp+' > '+qmout)
   mmfile= os.path.join(macrotarget,'MM.sce')
   return mmfile, qmout, yasara, qmxyz, atominfo,output_file
   
def mulliken(qmtxt, macrotarget):
    outputtxt = 'qm_charge.txt'
    with open(qmtxt, "r") as inifin, open(os.path.join(macrotarget, outputtxt), "w") as inifout:
        string = 'MULLIKEN ATOMIC CHARGES'
        lines_to_extract = False
        extracted_lines = []
        
        for line in inifin:
            if string in line:
                lines_to_extract = True
                continue  # Skip the line with 'MULLIKEN ATOMIC CHARGES'
            
            if lines_to_extract:
                if 'Sum of atomic charges:' in line:
                    break  # Stop extracting if we reach the sum line
                
                extracted_lines.append(line)
        
        # Extract only the last column and write it to the output file
        for line in extracted_lines[1:]:  # Skip the first two lines and the last one
            last_column_value = line.split()[-1]
            inifout.write(last_column_value + '\n')
    return outputtxt

def charge_assignment(macrotarget, yasara, mmfile,outputtxt,atominfo,newlyaddedatom_info):

   QM_MM_content= '''
txfile = '(MACROTARGET)/merged_qm_atom_info.txt'
Loadsce '(macrotarget)/MM.sce'
ForceField AMBER14,SetPar=Yes
Longrange None
Cutoff 10.50000
Interactions Bond,Angle,Dihedral,Planarity,Coulomb,VdW

for line in file (txfile)
  x,numero=split line
  print (x)
  print (numero)
  UnselectAll
  SelectAtom (numero)
  ChargeAtom selected, (x)

Temp 298K
TempCtrl SteepDes
TimeStep 2,1
Sim On      
simulation_time = 30


for j=1 to (simulation_time)
  Wait (j) #,Femtoseconds
  if (j)==(simulation_time)
    Sim off
    MakeTab MyTable,Dimensions=1
    for line in file (txfile)
      x,numero=split line
      SelectAtom (numero),Mode=Add
    SaveXYZ selected ,(MACROTARGET)/qm_mm_30.xyz,transform=Yes
    
Sim off
DelObj SimCELL    
SaveSce (MACROTARGET)/qm_mm.sce

exit  
 
'''
   f= open(atominfo,'r')
   data=f.readlines()
   data=''.join(data[1:])
   g=open(atominfo,'w+')
   g.write(data)
   g.close()
   with open(newlyaddedatom_info, 'r') as file:
       lines = file.readlines()

# Initialize an empty list to store the first column values
   first_column_values = []

# Iterate through the lines, skipping the header
   for line in lines[1:]:  # Skip the first line
    # Split the line by whitespace and get the first column value
       first_column_value = line.split()[0]
    # Append the first column value to the list
       first_column_values.append(int(first_column_value))
# Print the list to verify the result
   print(first_column_values)   
   delete_lines_from_file(outputtxt, first_column_values)
   remove_blank_lines(atominfo, atominfo)
   merged_output_file_path = os.path.join(macrotarget,'merged_qm_atom_info.txt')
   merge_files(outputtxt, atominfo, merged_output_file_path)
   qm_mm_macrofile= os.path.join(macrotarget,'qm_mm.mcr')
   qm_mm= open(qm_mm_macrofile,'w')
   qm_mm.write(str("MACROTARGET = '"+macrotarget+"'\n"))
   qm_mm.write(str(QM_MM_content))
   qm_mm.close()
   os.system(yasara+' '+qm_mm_macrofile)
   mdrun_input= os.path.join(macrotarget,'qm_mm.sce')
   return mdrun_input

 
def md_run(yasara, macrotarget,orcapath,mdrun_input):
   
   MDrun_content= '''
Loadsce '(macrotarget)/qm_mm.sce'
#Showmessage 'Load your structure'
#wait continuebutton
numeroobj= CountObj all
if numeroobj >0
  atomlist()= ListAtom Selected
  #MakeTab atomlistqm,Dimensions=1
  numero= Countatom selected
  #Tabulate (atomlist)
  #SaveTab atomlistqm,(MACROTARGET)/atom.txt,Format=Text,Columns=1,NumFormat=6.0f,atom_numero
 # MakeTab MyTable,Dimensions=1
  for n in atomlist()
    propatom (n),(n)
    SelectAtom (n),mode=add
    #propatom (n),(n)
  Delatom !selected
  #wait continuebutton
  AddHydObj 1
  ForceField AMBER14,SetPar=No
  Interactions Bond,Angle,Dihedral,Planarity,Coulomb,VdW
  #wait continuebutton
  refresh_numero()= ListAtom Selected 
  SaveXYZ selected, '(MACROTARGET)/QM.xyz'
  UnSelectAll
  charge= Chargeobj 1
  for i in refresh_numero()
    p=propatom (i)
    p= (00+p)
    if p == 0      
      #Tabulate (00+i)
      #Tabulate (00+charge)
      
      SelectAtom (i), Mode=Add #p=refresh_numero
    else
      print ('ok')#p= (00+p) 
  

#SaveTab MyTable,(MACROTARGET)/newadded.txt,Format=Text,Columns=2,NumFormat=6.0f,newly_added_Atom Charge_all
exit
  
''' 
   mdrunmacrofile= os.path.join(macrotarget,'mdrun.mcr')
   f= open(mdrunmacrofile,'w')
   f.write(str("MACROTARGET = '"+macrotarget+"'\n"))
   f.write(str(MDrun_content))
   f.close()  
   
   os.system(yasara+' '+mdrunmacrofile+' -txt')
   orca= os.path.join(orcapath,'orca')
   os.chdir(macrotarget)
   #input_file = os.path.join(macrotarget, 'newadded.txt')
   output_file = os.path.join(macrotarget, 'newadded.txt')
   #remove_blank_lines(input_file, output_file)
   with open(output_file, 'r') as file:
    # Read all lines
       lines = file.readlines()

 # Get the number of lines except the first line (header)
   line_count = len(lines) - 1
   second_column_first_value = lines[1].split()[1]
   charge_info = str(second_column_first_value)
   qminp= os.path.join(macrotarget,'QM.inp')
   qmout= os.path.join(macrotarget,'QM.out')
   qmxyz= os.path.join(macrotarget,'QM.xyz')
   f= open(qmxyz,'r')
   data=f.readlines()
   data=''.join(data[2:])
   #print(data)
   orcainp= open(qminp,'w+')
   orcainp.write('!PM3 RHF Opt')
   orcainp.write('\n\n* xyz  '+str(charge_info)+' 1 \n')
   orcainp.write(data+'*\n')
   orcainp.close()
   #os.chdir(yasarapath)
   #os.chdir(macrotarget)
   #time.sleep(5)
   os.system(orca+' '+qminp+' > '+qmout)
   print('QM optimization is in process..')
   mdrun_input= os.path.join(macrotarget,'qm_mm.sce')
   charge_opt_txt= mulliken(qmout, macrotarget)
   return charge_opt_txt,mdrun_input
   
   
 
def recharge_assignment(macrotarget, yasara, mdrun_input, charge_opt_txt,atominfo,newlyaddedatom_info,simulation_time):

   QM_MM_content= '''
txfile = '(MACROTARGET)/merged_qm_atom_info.txt'
Loadsce '(macrotarget)/qm_mm.sce'
ForceField AMBER14,SetPar=Yes
Longrange None
Cutoff 10.50000
Interactions Bond,Angle,Dihedral,Planarity,Coulomb,VdW
Temp 298K
TempCtrl Anneal
TimeStep 2,1
Sim On 
for line in file (txfile)
  x,numero=split line
  print (x)
  print (numero)
  UnselectAll
  SelectAtom (numero)
  ChargeAtom selected, (x)

     

for j=1 to (simulation_time)
  Wait (j) #,Femtoseconds
  if (j)==(simulation_time)
    Sim off
    MakeTab MyTable,Dimensions=1
    for line in file (txfile)
      x,numero=split line
      SelectAtom (numero),Mode=Add
    SaveXYZ selected ,(MACROTARGET)/qm_mm_30.xyz,transform=Yes
    
Sim off
DelObj SimCELL    
SaveSce (MACROTARGET)/qm_mm.sce
exit  
 
'''
   #f= open(atominfo,'r')
   #data=f.readlines()
   #data=''.join(data[1:])
   #g=open(atominfo,'w+')
   #g.write(data)
   #g.close()
   with open(newlyaddedatom_info, 'r') as file:
       lines = file.readlines()

# Initialize an empty list to store the first column values
   first_column_values = []

# Iterate through the lines, skipping the header
   for line in lines[1:]:  # Skip the first line
    # Split the line by whitespace and get the first column value
       first_column_value = line.split()[0]
    # Append the first column value to the list
       first_column_values.append(int(first_column_value))
# Print the list to verify the result
     
   delete_lines_from_file(charge_opt_txt, first_column_values)
   remove_blank_lines(atominfo, atominfo)
   #
   merged_output_file_path=os.path.join(macrotarget,'merged_qm_atom_info.txt')
   merge_files(charge_opt_txt, atominfo, merged_output_file_path)
   qm_mm_macrofile= os.path.join(macrotarget,'qm_mm.mcr')
   qm_mm= open(qm_mm_macrofile,'w')
   qm_mm.write(str("MACROTARGET = '"+macrotarget+"'\n"))
   qm_mm.write(str("simulation_time = '"+str(simulation_time)+"'\n"))
   qm_mm.write(str(QM_MM_content))
   qm_mm.close()
   os.system(yasara+' '+qm_mm_macrofile+ ' -txt')
   mdrun_input= os.path.join(macrotarget,'qm_mm.sce')
   return mdrun_input

 
 
       
#for initial single point charge assignment to the qm atoms and starting the MM simulation
mmfile, qmout, yasara, qmxyz, atominfo, newlyaddedatom_info  = loadstrcture(yasarapath, macrotarget,orcapath)
outputtxt= mulliken(qmout, macrotarget)
mdrun_input=charge_assignment(macrotarget, yasara, mmfile,outputtxt,atominfo,newlyaddedatom_info)

i= 0
simulation_time=int(simulation_time)
for i in range (0,simulation_time):
   print('cycle :'+str(i))
   charge_opt_txt,mdrun_input = md_run(yasara, macrotarget,orcapath,mdrun_input)
   mdrun_input=recharge_assignment(macrotarget, yasara, mdrun_input, charge_opt_txt,atominfo,newlyaddedatom_info,simulation_time)
   print('FINISHED')






