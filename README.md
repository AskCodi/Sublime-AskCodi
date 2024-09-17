## Accelerate Your Development Workflow With AskCodi
**[AskCodi](https://askcodi.com)** is an AI code assistant developed by Assistiv.ai, that **facilitates coders** to code faster by providing following features:<br/>
**1. Chat with Codi AI (Ask AI to code),**<br/>
**2. Code suggestions for natural language (Ask AI to code),**<br/>
**3. Time complexity for your code,**<br/>
**4. Document Code.**<br/>
**5. Explain Code,**<br/>
**6. Test Code.**<br/>
<br/>
Whether you are new to coding or a professional, working individually or in a team, AskCodi helps save time by answering your queries in your favourite IDE.
<br/>


## Installation

1. Install [Package Control](https://packagecontrol.io/installation).

2. In Sublime, press `ctrl+shift+p`(Windows, Linux) or `cmd+shift+p`(OS X).

3. Type `install`, then press `enter` with `Package Control: Install Package` selected.

4. Type `askcodi`, then press `enter` with the `AskCodi` plugin selected.

5. AskCodi will prompt to add an API key.

6. Go to[Webapp](https://askcodi.com), sign in and in your account settings, copy the API key in Sublime Text.



## Usage

**1. Generate Code:** Write your query as comment or statement. Select the query, right click and go to AskCodi. Click on Generate Code and wait for Codi panel to open and display the results.

**2. Document Code:** Select the code, right click and go to AskCodi. Click on Document Code and wait for Codi panel to open and display the results.

**3. Test Code:** Select the code, right click and go to AskCodi. Click on Test Code and wait for Codi panel to open and display the results.

**3. Chat:** Complete code can be triggered using hot keys `ctrl + alt + c` or `ctrl + option + c` , or right click and go to AskCodi. Whether you are writing a statement or code, complete code can be triggered directly using the hot key to complete the code or even comments.

**4. Explain Code:** Select the code, right click and go to AskCodi. Click on Explain Code and a Codi panel opens. Keep the default text as it is to get the time complexity of the selected code. Delete and either provide a different information if you want(like a library)or leave it empty, and hit enter to get code explanation. Wait for Codi panel to open and display the results.

### API key

On installation, AskCodi will prompt to add the API key. Get the API key from [Webapp](https://askcodi.com), sign in and in your account settings, copy the API key in Sublime Text.

> [!NOTE]
> You can manually set API key via command pallete (press `ctrl+shift+p`(Windows, Linux) or `cmd+shift+p`(OS X)) and search for `AskCodi: Set API Key` or, by right clicking on editor, `AskCodi Defaults` -> `Set API key`.


### Model(llm) Selection

By default, AskCodi uses `Base` llm for requests. you can change the default model via command pallete (press `ctrl+shift+p`(Windows, Linux) or `cmd+shift+p`(OS X)) and search for `AskCodi: Select Model` or, by right clicking on editor, `AskCodi Defaults` -> `Select Model`

Alternatively, AskCodi plugin has model in settings file. To set your default model, open the settings within `Preferences` -> `Package Settings` -> `AskCodi` -> `Settings` and paste your API key in the api_key property, as follows:

```JSON
{
    "model": "Base",
}
```


### Chat history management

You can reset the chat history via command pallete (press `ctrl+shift+p`(Windows, Linux) or `cmd+shift+p`(OS X)) and search for `AskCodi: Reset chat history` or, by right clicking on editor, `AskCodi Defaults` -> `Reset Chat`.

## Settings

The AskCodi plugin has a settings file where you can set your API key. To set your API key, open the settings within `Preferences` -> `Package Settings` -> `AskCodi` -> `Settings` and paste your API key in the api_key property, as follows:

```JSON
{
    "api_key": "your-api-key",
}
```

## Key bindings

You can bind keys for a given plugin command in `Preferences` -> `Package Settings` -> `AskCodi` -> `Key Bindings`. For example you can bind "Chat" command like this:

```json
{
    "keys": ["ctrl+alt+c"],
    "command": "chat"
},
```

### Markdown syntax with syntax highlight support

> [!IMPORTANT]
> It's highly recommended to install the [`MultimarkdownEditing`](https://sublimetext-markdown.github.io/MarkdownEditing/) to apply broader set of languages with syntax highlighting.



## Links

Join our  [discord](https://discord.gg/sXU4F6XfAx) community to stay updated on the changes and talk to the community.