# creating JHP menu
import MaxPlus
import sys

# ------------------------------ import JHP script ------------------------------

jhpScriptDir = MaxPlus.PathManager.GetScriptsDir() + "\JHP"
sys.path.append(jhpScriptDir)

import changeFormatToUE4
import UE4BoneMapper

menuName = "JHP"

# ------------------------------ main ------------------------------

def proxy_AnimFormatChanger():
	changeFormatToUE4.openAnimFormatChangeForUE4()

def proxy_UE4BoneMapper():
	UE4BoneMapper.openBoneMapperWindow()

# check same name
if MaxPlus.MenuManager.MenuExists(menuName ):
	MaxPlus.MenuManager.UnregisterMenu(menuName)

changeFormat_action = MaxPlus.ActionFactory.Create(
"JHPUtils",
"ChangeFormat2UE4",
proxy_AnimFormatChanger
)

boneMapper_action = MaxPlus.ActionFactory.Create(
"JHPUtils",
"UE4BoneMapper",
proxy_UE4BoneMapper
)

mb = MaxPlus.MenuBuilder(menuName)

mb.AddItem(changeFormat_action)
mb.AddItem(boneMapper_action)
#mb.AddSeparator()

menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())