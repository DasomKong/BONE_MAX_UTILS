/* ver 1.0 */

macroScript JHP_Tools
category:"(JHP)"
toolTip:"JHPTools"
buttonText:"JHPTools"
(
	on execute do
	(
		/*
		local sFile = (GetDir #scripts) + "/ReimUI.mse" 
		
		print sFile
		
		python.ExecuteFile @"C:\Users\JEONGWOO\Desktop\menuCreate.py"
		*/
	)	
)

sFile = (GetDir #scripts) + "\JHP\menuCreate.py" 

if(sFile != undefined) then
(
	python.ExecuteFile sFile
)
else
(
	messageBox "Can't create JHP-Menu"
)
