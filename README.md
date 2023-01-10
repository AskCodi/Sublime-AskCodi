## Accelerate Your Development Workflow With AskCodi
**[AskCodi](https://askcodi.com)** is an AI code assistant developed by Assistiv.ai, that **facilitates coders** to code faster by providing following features:<br/>
**1. Auto-complete (only in VS Code),**<br/>
**2. Code suggestions for natural language (Ask AI to code),**<br/>
**3. Time complexity for your code,**<br/>
**4. Document Code.**<br/>
**5. Explain Code,**<br/>
**6. Complete Code (Manually triggerd, works same as auto-complete),**<br/>
**7. Test Code.**<br/>
<br/>
Whether you are new to coding or a professional, working individually or in a team, AskCodi helps save time by answering your queries in your favourite IDE.
<br/>

## Team learning
With the support of teams, you can accelerate the process by sharing suggestions with your team or the community. AskCodi extension is integrated along with webapp version. Any code generated is reflected in the codebase. You can change the workspace from the webapp for the extension and segregate your codebase.

## Installation

1. Install [Package Control](https://packagecontrol.io/installation).

2. In Sublime, press `ctrl+shift+p`(Windows, Linux) or `cmd+shift+p`(OS X).

3. Type `install`, then press `enter` with `Package Control: Install Package` selected.

4. Type `askcodi`, then press `enter` with the `AskCodi` plugin selected.

5. Follow the sign-in process to authenticate your device..

6. Use Sublime and Codi will be ready to pair program with you. Your code generated will be in your codebase that can be explored in [Webapp](https://app.askcodi.com).


## Usage

**1. Generate Code:** Write your query as comment or statement. Select the query, right click and go to AskCodi. Click on Generate Code and wait for bottom panel to open and display the results.

**2. Document Code:** Select the code, right click and go to AskCodi. Click on Document Code and wait for bottom panel to open and display the results.

**3. Test Code:** Select the code, right click and go to AskCodi. Click on Test Code and wait for bottom panel to open and display the results.

**3. Complete Code:** Complete code can be triggered using hot keys `ctrl + alt + 1` or `ctrl + option + 1` only. Whether you are writing a statement or code, complete code can be triggered directly using the hot key to complete the code or even comments.

**4. Explain Code:** Select the code, right click and go to AskCodi. Click on Explain Code and a bottom dialogue box opens. Keep the default text as it is to get the time complexity of the selected code. Delete and either provide a different information if you want(like a library)or leave it empty, and hit enter to get code explanation. Wait for bottom panel to open and display the results.


## How it works

1. AskCodi uses OpenAI GPT3 to generate suggestions.

2. For the **context, Codi uses 512 characters before the selected query, or position of cursor/caret and uses that code to provide relavant suggestions. You can turn off the context from the user settings file (see section "Change user settings") by changing from "true" to "false"** Please note, AskCodi does not save this context, however it is recommended that you do not include any sensitive data in the context or query. Also, with context "off", **Complete code** application won't work.

3. AskCodi sends the context code(if on in settings) and the selected text/code to the servers to generate suggestions.

4. The generated suggestion and query is saved on AskCodi servers to provide a codebase feature, which is only visible to the user(s) in the workspace they authenticated their device with. Only in case you chose "Community" workspace, it is visible to rest of the community.

## Change user settings

**Mac:** Goto Settings => Preferences => Package Settings => AskCodi => User - Settings

**Windows:** Goto Preferences => User - Settings

**Ubuntu:** Goto Preferences => User - Settings

Edit the file as per preferences, the acceptable values are **true** or **false** for each of the setting, and save the file.


## Change Key bindings

**Mac:** Goto Settings => Preferences => Package Settings => AskCodi => Key - Bindings 

**Windows:** Goto Preferences => Key - Bindings 

**Ubuntu:** Goto Preferences => Key - Bindings 

Make the desired changes and save the file.


## Links

Join our  [discord](https://discord.gg/sXU4F6XfAx) community to stay updated on the changes and talk to the community.