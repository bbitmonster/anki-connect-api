# Anki-Connect

Anki-Connect enables external applications such as [Yomichan](https://foosoft.net/projects/yomichan/) to communicate
with [Anki](https://apps.ankiweb.net/) over a simple HTTP API. Its capabilities include executing queries against the
user's card deck, automatically creating new cards, and more. Anki-Connect is compatible with the latest stable (2.1.x)
releases of Anki; older versions (2.0.x and below) are no longer supported.

## Installation

The installation process is similar to other Anki plugins and can be accomplished in three steps:

1.  Open the `Install Add-on` dialog by selecting `Tools` | `Add-ons` | `Get Add-ons...` in Anki.
2.  Input [2055492159](https://ankiweb.net/shared/info/2055492159) into the text box labeled `Code` and press the `OK` button to proceed.
3.  Restart Anki when prompted to do so in order to complete the installation of Anki-Connect.

Anki must be kept running in the background in order for other applications to be able to use Anki-Connect. You can
verify that Anki-Connect is running at any time by accessing `localhost:8765` in your browser. If the server is running,
you will see the message `Anki-Connect` displayed in your browser window.

### Notes for Windows Users

Windows users may see a firewall nag dialog box appear on Anki startup. This occurs because Anki-Connect runs a local
HTTP server in order to enable other applications to connect to it. The host application, Anki, must be unblocked for
this plugin to function correctly.

### Notes for MacOS Users

Starting with [Mac OS X Mavericks](https://en.wikipedia.org/wiki/OS_X_Mavericks), a feature named *App Nap* has been
introduced to the operating system. This feature causes certain applications which are open (but not visible) to be
placed in a suspended state. As this behavior causes Anki-Connect to stop working while you have another window in the
foreground, App Nap should be disabled for Anki:

1.  Start the Terminal application.
2.  Execute the following commands in the terminal window:
    ```bash
    defaults write net.ankiweb.dtop NSAppSleepDisabled -bool true
    defaults write net.ichi2.anki NSAppSleepDisabled -bool true
    defaults write org.qt-project.Qt.QtWebEngineCore NSAppSleepDisabled -bool true
    ```
3.  Restart Anki.

## Application Interface for Developers

Anki-Connect exposes internal Anki features to external applications via an easy to use API. After being installed, this
plugin will start an HTTP server on port 8765 whenever Anki is launched. Other applications (including browser
extensions) can then communicate with it via HTTP requests.

By default, Anki-Connect will only bind the HTTP server to the `127.0.0.1` IP address, so that you will only be able to
access it from the same host on which it is running. If you need to access it over a network, you can change the
binding address in the configuration. Go to Tools->Add-ons->AnkiConnect->Config and change the "webBindAddress"
value. For example, you can set it to `0.0.0.0` in order to bind it to all network interfaces on your host. This also
requires a restart for Anki.

### Sample Invocation

Every request consists of a JSON-encoded object containing an `action`, a `version`, contextual `params`, and a `key`
value used for authentication (which is optional and can be omitted by default). Anki-Connect will respond with an
object containing two fields: `result` and `error`. The `result` field contains the return value of the executed API,
and the `error` field is a description of any exception thrown during API execution (the value `null` is used if
execution completed successfully).

*Sample successful response*:
```json
{"result": ["Default", "Filtered Deck 1"], "error": null}
```

*Samples of failed responses*:
```json
{"result": null, "error": "unsupported action"}
```
```json
{"result": null, "error": "guiBrowse() got an unexpected keyword argument 'foobar'"}
```

For compatibility with clients designed to work with older versions of Anki-Connect, failing to provide a `version`
field in the request will make the version default to 4. Furthermore, when the provided version is level 4 or below, the
API response will only contain the value of the `result`; no `error` field is available for error handling.

You can use whatever language or tool you like to issue request to Anki-Connect, but a couple of simple examples are
included below as reference.

#### Curl

```bash
curl localhost:8765 -X POST -d '{"action": "deckNames", "version": 6}'
```

#### Powershell

```powershell
(Invoke-RestMethod -Uri http://localhost:8765 -Method Post -Body '{"action": "deckNames", "version": 6}').result
```

#### Python

```python
import json
import urllib.request

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

invoke('createDeck', deck='test1')
result = invoke('deckNames')
print('got list of decks: {}'.format(result))
```

#### JavaScript

```javascript
function invoke(action, version, params={}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('error', () => reject('failed to issue request'));
        xhr.addEventListener('load', () => {
            try {
                const response = JSON.parse(xhr.responseText);
                if (Object.getOwnPropertyNames(response).length != 2) {
                    throw 'response has an unexpected number of fields';
                }
                if (!response.hasOwnProperty('error')) {
                    throw 'response is missing required error field';
                }
                if (!response.hasOwnProperty('result')) {
                    throw 'response is missing required result field';
                }
                if (response.error) {
                    throw response.error;
                }
                resolve(response.result);
            } catch (e) {
                reject(e);
            }
        });

        xhr.open('POST', 'http://127.0.0.1:8765');
        xhr.send(JSON.stringify({action, version, params}));
    });
}

await invoke('createDeck', 6, {deck: 'test1'});
const result = await invoke('deckNames', 6);
console.log(`got list of decks: ${result}`);
```

### Authentication

Anki-Connect supports requiring authentication in order to make API requests.
This support is *disabled* by default, but can be enabled by setting the `apiKey` field of Anki-Config's settings (Tools->Add-ons->AnkiConnect->Config) to a desired string.
If you have done so, you should see the [`requestPermission`](#requestpermission) API request return `true` for `requireApiKey`.
You then must include an additional parameter called `key` in any further API request bodies, whose value must match the configured API key.

### Hey, could you add a new action to support $FEATURE?

The primary goal for Anki-Connect was to support real-time flash card creation from the
[Yomichan](https://foosoft.net/projects/yomichan/) browser extension. The current API provides all the required actions
to make this happen. I recognise that the role of Anki-Connect has evolved from this original vision, and I am happy to
review new feature requests.

With that said, *this project operates on a self-serve model*. If you would like a new feature, create a PR. I'll review
it and if it looks good, it will be merged in. *Requests to add new features without accompanying pull requests will not
be serviced*. Make sure that your pull request meets the following criteria:

*   Attempt to match style of the surrounding code.
*   Have accompanying documentation with examples.
*   Have accompanying tests that verify operation.
*   Implement features useful in other applications.

## Supported Actions

Documentation for currently supported actions is split up by category and is referenced below. Note that deprecated APIs
will continue to function despite not being listed on this page as long as your request is labeled with a version number
corresponding to when the API was available for use.
Search parameters are passed to Anki, check the docs for more information: https://docs.ankiweb.net/searching.html

* [Card Actions](#card-actions)
* [Deck Actions](#deck-actions)
* [Graphical Actions](#graphical-actions)
* [Media Actions](#media-actions)
* [Miscellaneous Actions](#miscellaneous-actions)
* [Model Actions](#model-actions)
* [Note Actions](#note-actions)
* [Statistic Actions](#statistic-actions)

---

