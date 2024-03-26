
<!-- This file is auto-generated from <anki_connect.py>, do not edit it by hand. -->

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

### Card Actions

```python
def getEaseFactors(cards):
```
*   Returns an array with the ease factor for each of the given cards (in the same
    order).

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getEaseFactors([1483959291685, 1483959293217])
    [4100, 3900]
    ```
    </details>

```python
def setEaseFactors(cards, easeFactors):
```
*   Sets ease factor of cards by card ID; returns `True` if successful (all cards
    existed) or `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> setEaseFactors([1483959291685, 1483959293217], [4100, 3900])
    [True, True]
    ```
    </details>

```python
def setSpecificValueOfCard(card, keys, newValues):
```
*   Sets specific value of a single card. Given the risk of wreaking havor in the
    database when changing some of the values of a card, some of the keys require the
    argument "warning_check" set to True. This can be used to set a card's flag, change
    it's ease factor, change the review order in a filtered deck and change the column
    "data" (not currently used by anki apparantly), and many other values. A list of
    values and explanation of their respective utility can be found at [AnkiDroid's
    wiki](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure).

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> setSpecificValueOfCard(1483959291685, ["flags", "odue"], ["1", "-100"])
    [True, True]
    ```
    </details>

```python
def suspend(cards):
```
*   Suspend cards by card ID; returns `True` if successful (at least one card wasn't
    already suspended) or `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> suspend([1483959291685, 1483959293217])
    True
    ```
    </details>

```python
def unsuspend(cards):
```
*   Unsuspend cards by card ID; returns `True` if successful (at least one card was
    previously suspended) or `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> unsuspend([1483959291685, 1483959293217])
    True
    ```
    </details>

```python
def suspended(card):
```
*   Check if card is suspended by its ID. Returns `True` if suspended, `False`
    otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> suspended(1483959293217)
    True
    ```
    </details>

```python
def areSuspended(cards):
```
*   Returns an array indicating whether each of the given cards is suspended (in the
    same order). If card doesn't exist returns `None`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> areSuspended([1483959291685, 1483959293217, 1234567891234])
    [False, True, None]
    ```
    </details>

```python
def areDue(cards):
```
*   Returns an array indicating whether each of the given cards is due (in the same
    order). *Note*: cards in the learning queue with a large interval (over 20 minutes)
    are treated as not due until the time of their interval has passed, to match the way
    Anki treats them when reviewing.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> areDue([1483959291685, 1483959293217])
    [False, True]
    ```
    </details>

```python
def getIntervals(cards, complete):
```
*   Returns an array of the most recent intervals for each given card ID, or a
    2-dimensional array of all the intervals for each given card ID when `complete` is
    `True`. Negative intervals are in seconds and positive intervals in days.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getIntervals([1502298033753, 1502298036657])
    [-14400, 3]
    ```
    </details>

```python
def findCards(query):
```
*   Returns an array of card IDs for a given query. Functionally identical to
    `guiBrowse` but doesn't use the GUI for better performance.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> findCards("deck:current")
    [1494723142483, 1494703460437, 1494703479525]
    ```
    </details>

```python
def cardsToNotes(cards):
```
*   Returns an unordered array of note IDs for the given card IDs. For cards with the
    same note, the ID is only given once in the array.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> cardsToNotes([1502098034045, 1502098034048, 1502298033753])
    [1502098029797, 1502298025183]
    ```
    </details>

```python
def cardsModTime(cards):
```
*   Returns a list of objects containings for each card ID the modification time. This
    function is about 15 times faster than executing `cardsInfo`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> cardsModTime([1498938915662, 1502098034048])
    [{"cardId": 1498938915662, "mod": 1629454092}]
    ```
    </details>

```python
def cardsInfo(cards):
```
*   Returns a list of objects containing for each card ID the card fields, front and
    back sides including CSS, note type, the note that the card belongs to, and deck name,
    last modification timestamp as well as ease and interval.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> cardsInfo([1498938915662, 1502098034048])
    [
        {
            "answer": "back content",
            "question": "front content",
            "deckName": "Default",
            "modelName": "Basic",
            "fieldOrder": 1,
            "fields": {
                "Front": {"value": "front content", "order": 0},
                "Back": {"value": "back content", "order": 1},
            },
            "css": "p {font-family:Arial;}",
            "cardId": 1498938915662,
            "interval": 16,
            "note": 1502298033753,
            "ord": 1,
            "type": 0,
            "queue": 0,
            "due": 1,
            "reps": 1,
            "lapses": 0,
            "left": 6,
            "mod": 1629454092,
        },
        {
            "answer": "back content",
            "question": "front content",
            "deckName": "Default",
            "modelName": "Basic",
            "fieldOrder": 0,
            "fields": {
                "Front": {"value": "front content", "order": 0},
                "Back": {"value": "back content", "order": 1},
            },
            "css": "p {font-family:Arial;}",
            "cardId": 1502098034048,
            "interval": 23,
            "note": 1502298033753,
            "ord": 1,
            "type": 0,
            "queue": 0,
            "due": 1,
            "reps": 1,
            "lapses": 0,
            "left": 6,
        },
    ]
    ```
    </details>

```python
def forgetCards(cards):
```
*   Forget cards, making the cards new again.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> forgetCards([1498938915662, 1502098034048])
    None
    ```
    </details>

```python
def relearnCards(cards):
```
*   Make cards be "relearning".

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> relearnCards([1498938915662, 1502098034048])
    None
    ```
    </details>

```python
def answerCards(answers):
```
*   Answer cards. Ease is between 1 (Again) and 4 (Easy). Will start the timer
    immediately before answering. Returns `True` if card exists, `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> answerCards(
    ...     [{"cardId": 1498938915662, "ease": 2}, {"cardId": 1502098034048, "ease": 4}]
    ... )
    [True, True]
    ```
    </details>

### Deck Actions

```python
def deckNames():
```
*   Gets the complete list of deck names for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> deckNames()
    ["Default"]
    ```
    </details>

```python
def deckNamesAndIds():
```
*   Gets the complete list of deck names and their respective IDs for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> deckNamesAndIds()
    {"Default": 1}
    ```
    </details>

```python
def getDecks(cards):
```
*   Accepts an array of card IDs and returns an object with each deck name as a key,
    and its value an array of the given cards which belong to it.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getDecks([1502298036657, 1502298033753, 1502032366472])
    {"Default": [1502032366472], "Japanese::JLPT N3": [1502298036657, 1502298033753]}
    ```
    </details>

```python
def createDeck(deck):
```
*   Create a new empty deck. Will not overwrite a deck that exists with the same name.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> createDeck("Japanese::Tokyo")
    1519323742721
    ```
    </details>

```python
def changeDeck(cards, deck):
```
*   Moves cards with the given IDs to a different deck, creating the deck if it doesn't
    exist yet.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> changeDeck([1502098034045, 1502098034048, 1502298033753], "Japanese::JLPT N3")
    None
    ```
    </details>

```python
def deleteDecks(decks, cardsToo):
```
*   Deletes decks with the given names. The argument `cardsToo` *must* be specified and
    set to `True`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> deleteDecks(["Japanese::JLPT N5", "Easy Spanish"], True)
    None
    ```
    </details>

```python
def getDeckConfig(deck):
```
*   Gets the configuration group object for the given deck.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getDeckConfig("Default")
    {
        "lapse": {
            "leechFails": 8,
            "delays": [10],
            "minInt": 1,
            "leechAction": 0,
            "mult": 0,
        },
        "dyn": False,
        "autoplay": True,
        "mod": 1502970872,
        "id": 1,
        "maxTaken": 60,
        "new": {
            "bury": True,
            "order": 1,
            "initialFactor": 2500,
            "perDay": 20,
            "delays": [1, 10],
            "separate": True,
            "ints": [1, 4, 7],
        },
        "name": "Default",
        "rev": {
            "bury": True,
            "ivlFct": 1,
            "ease4": 1.3,
            "maxIvl": 36500,
            "perDay": 100,
            "minSpace": 1,
            "fuzz": 0.05,
        },
        "timer": 0,
        "replayq": True,
        "usn": -1,
    }
    ```
    </details>

```python
def saveDeckConfig(config):
```
*   Saves the given configuration group, returning `True` on success or `False` if the
    ID of the configuration group is invalid (such as when it does not exist).

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> saveDeckConfig(
    ...     {
    ...         "lapse": {
    ...             "leechFails": 8,
    ...             "delays": [10],
    ...             "minInt": 1,
    ...             "leechAction": 0,
    ...             "mult": 0,
    ...         },
    ...         "dyn": False,
    ...         "autoplay": True,
    ...         "mod": 1502970872,
    ...         "id": 1,
    ...         "maxTaken": 60,
    ...         "new": {
    ...             "bury": True,
    ...             "order": 1,
    ...             "initialFactor": 2500,
    ...             "perDay": 20,
    ...             "delays": [1, 10],
    ...             "separate": True,
    ...             "ints": [1, 4, 7],
    ...         },
    ...         "name": "Default",
    ...         "rev": {
    ...             "bury": True,
    ...             "ivlFct": 1,
    ...             "ease4": 1.3,
    ...             "maxIvl": 36500,
    ...             "perDay": 100,
    ...             "minSpace": 1,
    ...             "fuzz": 0.05,
    ...         },
    ...         "timer": 0,
    ...         "replayq": True,
    ...         "usn": -1,
    ...     }
    ... )
    True
    ```
    </details>

```python
def setDeckConfigId(decks, configId):
```
*   Changes the configuration group for the given decks to the one with the given ID.
    Returns `True` on success or `False` if the given configuration group or any of the
    given decks do not exist.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> setDeckConfigId(["Default"], 1)
    True
    ```
    </details>

```python
def cloneDeckConfigId(name, cloneFrom):
```
*   Creates a new configuration group with the given name, cloning from the group with
    the given ID, or from the default group if this is unspecified. Returns the ID of the
    new configuration group, or `False` if the specified group to clone from does not
    exist.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> cloneDeckConfigId("Copy of Default", 1)
    1502972374573
    ```
    </details>

```python
def removeDeckConfigId(configId):
```
*   Removes the configuration group with the given ID, returning `True` if successful,
    or `False` if attempting to remove either the default configuration group (ID = 1) or
    a configuration group that does not exist.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> removeDeckConfigId(1502972374573)
    True
    ```
    </details>

```python
def getDeckStats(decks):
```
*   Gets statistics such as total cards and cards due for the given decks.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getDeckStats(["Japanese::JLPT N5", "Easy Spanish"])
    {
        "1651445861967": {
            "deck_id": 1651445861967,
            "name": "Japanese::JLPT N5",
            "new_count": 20,
            "learn_count": 0,
            "review_count": 0,
            "total_in_deck": 1506,
        },
        "1651445861960": {
            "deck_id": 1651445861960,
            "name": "Easy Spanish",
            "new_count": 26,
            "learn_count": 10,
            "review_count": 5,
            "total_in_deck": 852,
        },
    }
    ```
    </details>

### Graphical Actions

```python
def guiBrowse(query, reorderCards):
```
*   Invokes the *Card Browser* dialog and searches for a given query. Returns an array
    of identifiers of the cards that were found. Query syntax is [documented
    here](https://docs.ankiweb.net/searching.html).

    Optionally, the `reorderCards` property can be provided to reorder the cards shown in
    the *Card Browser*. This is an array including the `order` and `columnId` objects.
    `order` can be either `ascending` or `descending` while `columnId` can be one of
    several column identifiers (as documented in the [Anki source
    code](https://github.com/ankitects/anki/blob/main/rslib/src/browser_table.rs)). The
    specified column needs to be visible in the *Card Browser*.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiBrowse("deck:current", {"order": "descending", "columnId": "noteCrt"})
    [1494723142483, 1494703460437, 1494703479525]
    ```
    </details>

```python
def guiSelectNote(note):
```
*   Finds the open instance of the *Card Browser* dialog and selects a note given a
    note identifier. Returns `True` if the *Card Browser* is open, `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiSelectNote(1494723142483)
    True
    ```
    </details>

```python
def guiSelectedNotes():
```
*   Finds the open instance of the *Card Browser* dialog and returns an array of
    identifiers of the notes that are selected. Returns an empty list if the browser is
    not open.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiSelectedNotes()
    [1494723142483, 1494703460437, 1494703479525]
    ```
    </details>

```python
def guiAddCards(note):
```
*   Invokes the *Add Cards* dialog, presets the note using the given deck and model,
    with the provided field values and tags. Invoking it multiple times closes the old
    window and _reopen the window_ with the new provided values.

    Audio, video, and picture files can be embedded into the fields via the `audio`,
    `video`, and `picture` keys, respectively. Refer to the documentation of `addNote` and
    `storeMediaFile` for an explanation of these fields.

    The result is the ID of the note which would be added, if the user chose to confirm
    the *Add Cards* dialogue.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiAddCards(
    ...     {
    ...         "deckName": "Default",
    ...         "modelName": "Cloze",
    ...         "fields": {
    ...             "Text": "The capital of Romania is {{c1::Bucharest}}",
    ...             "Extra": "Romania is a country in Europe",
    ...         },
    ...         "tags": ["countries"],
    ...         "picture": [
    ...             {
    ...                 "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/EU-Romania.svg/285px-EU-Romania.svg.png",
    ...                 "filename": "romania.png",
    ...                 "fields": ["Extra"],
    ...             }
    ...         ],
    ...     }
    ... )
    1496198395707
    ```
    </details>

```python
def guiEditNote(note):
```
*   Opens the *Edit* dialog with a note corresponding to given note ID. The dialog is
    similar to the *Edit Current* dialog, but:

    * has a Preview button to preview the cards for the note
    * has a Browse button to open the browser with these cards
    * has Previous/Back buttons to navigate the history of the dialog
    * has no bar with the Close button

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiEditNote(1649198355435)
    None
    ```
    </details>

```python
def guiCurrentCard():
```
*   Returns information about the current card or `None` if not in review mode.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiCurrentCard()
    {
        "answer": "back content",
        "question": "front content",
        "deckName": "Default",
        "modelName": "Basic",
        "fieldOrder": 0,
        "fields": {
            "Front": {"value": "front content", "order": 0},
            "Back": {"value": "back content", "order": 1},
        },
        "template": "Forward",
        "cardId": 1498938915662,
        "buttons": [1, 2, 3],
        "nextReviews": ["<1m", "<10m", "4d"],
    }
    ```
    </details>

```python
def guiStartCardTimer():
```
*   Starts or resets the `timerStarted` value for the current card. This is useful for
    deferring the start time to when it is displayed via the API, allowing the recorded
    time taken to answer the card to be more accurate when calling `guiAnswerCard`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiStartCardTimer()
    True
    ```
    </details>

```python
def guiShowQuestion():
```
*   Shows question text for the current card; returns `True` if in review mode or
    `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiShowQuestion()
    True
    ```
    </details>

```python
def guiShowAnswer():
```
*   Shows answer text for the current card; returns `True` if in review mode or `False`
    otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiShowAnswer()
    True
    ```
    </details>

```python
def guiAnswerCard(ease):
```
*   Answers the current card; returns `True` if succeeded or `False` otherwise. Note
    that the answer for the current card must be displayed before before any answer can be
    accepted by Anki.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiAnswerCard(1)
    True
    ```
    </details>

```python
def guiUndo():
```
*   Undo the last action / card; returns `True` if succeeded or `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiUndo()
    True
    ```
    </details>

```python
def guiDeckOverview(name):
```
*   Opens the *Deck Overview* dialog for the deck with the given name; returns `True`
    if succeeded or `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiDeckOverview("Default")
    True
    ```
    </details>

```python
def guiDeckBrowser():
```
*   Opens the *Deck Browser* dialog.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiDeckBrowser()
    None
    ```
    </details>

```python
def guiDeckReview(name):
```
*   Starts review for the deck with the given name; returns `True` if succeeded or
    `False` otherwise.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiDeckReview("Default")
    True
    ```
    </details>

```python
def guiImportFile(path):
```
*   Invokes the *Import... (Ctrl+Shift+I)* dialog with an optional file path. Brings up
    the dialog for user to review the import. Supports all file types that Anki supports.
    Brings open file dialog if no path is provided. Forward slashes must be used in the
    path on Windows. Only supported for Anki 2.1.52+.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiImportFile("C:/Users/Desktop/cards.txt")
    None
    ```
    </details>

```python
def guiExitAnki():
```
*   Schedules a request to gracefully close Anki. This operation is asynchronous, so it
    will return immediately and won't wait until the Anki process actually terminates.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiExitAnki()
    None
    ```
    </details>

```python
def guiCheckDatabase():
```
*   Requests a database check, but returns immediately without waiting for the check to
    complete. Therefore, the action will always return `True` even if errors are detected
    during the database check.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> guiCheckDatabase()
    True
    ```
    </details>

### Media Actions

```python
def storeMediaFile(filename):
```
*   Stores a file with the specified base64-encoded contents inside the media folder.
    Alternatively you can specify a absolute file path, or a url from where the file shell
    be downloaded. If more than one of `data`, `path` and `url` are provided, the `data`
    field will be used first, then `path`, and finally `url`. To prevent Anki from
    removing files not used by any cards (e.g. for configuration files), prefix the
    filename with an underscore. These files are still synchronized to AnkiWeb. Any
    existing file with the same name is deleted by default. Set `deleteExisting` to false
    to prevent that by [letting Anki give the new file a non-conflicting
    name](https://github.com/ankitects/anki/blob/aeba725d3ea9628c73300648f748140db3fdd5ed/rslib/src/media/files.rs#L194).

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> storeMediaFile("_hello.txt", "SGVsbG8sIHdvcmxkIQ==")
    "_hello.txt"
    ```
    </details>

```python
def retrieveMediaFile(filename):
```
*   Retrieves the base64-encoded contents of the specified file, returning `False` if
    the file does not exist.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> retrieveMediaFile("_hello.txt")
    "SGVsbG8sIHdvcmxkIQ=="
    ```
    </details>

```python
def getMediaFilesNames(pattern):
```
*   Gets the names of media files matched the pattern. Returning all names by default.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getMediaFilesNames("_hell*.txt")
    ["_hello.txt"]
    ```
    </details>

```python
def getMediaDirPath():
```
*   Gets the full path to the `collection.media` folder of the currently opened
    profile.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getMediaDirPath()
    "/home/user/.local/share/Anki2/Main/collection.media"
    ```
    </details>

```python
def deleteMediaFile(filename):
```
*   Deletes the specified file inside the media folder.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> deleteMediaFile("_hello.txt")
    None
    ```
    </details>

### Miscellaneous Actions

```python
def requestPermission():
```
*   Requests permission to use the API exposed by this plugin. This method does not
    require the API key, and is the only one that accepts requests from any origin; the
    other methods only accept requests from trusted origins, which are listed under
    `webCorsOriginList` in the add-on config. `localhost` is trusted by default.

    Calling this method from an untrusted origin will display a popup in Anki asking the
    user whether they want to allow your origin to use the API; calls from trusted origins
    will return the result without displaying the popup. When denying permission, the user
    may also choose to ignore further permission requests from that origin. These origins
    end up in the `ignoreOriginList`, editable via the add-on config.

    The result always contains the `permission` field, which in turn contains either the
    string `granted` or `denied`, corresponding to whether your origin is trusted. If your
    origin is trusted, the fields `requireApiKey` (`True` if required) and `version` will
    also be returned.

    This should be the first call you make to make sure that your application and Anki-
    Connect are able to communicate properly with each other. New versions of Anki-Connect
    are backwards compatible; as long as you are using actions which are available in the
    reported Anki-Connect version or earlier, everything should work fine.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> requestPermission()
    {"permission": "granted", "requireApiKey": False, "version": 6}
    ```
    </details>

```python
def version():
```
*   Gets the version of the API exposed by this plugin. Currently versions `1` through
    `6` are defined.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> version()
    6
    ```
    </details>

```python
def apiReflect(scopes, actions):
```
*   Gets information about the AnkiConnect APIs available. The request supports the
    following params:

    * `scopes` - An array of scopes to get reflection information about. The only
    currently supported value is `"actions"`.
    * `actions` - Either `None` or an array of API method names to check for. If the value
    is `None`, the result will list all of the available API actions. If the value is an
    array of strings, the result will only contain actions which were in this array.

    The result will contain a list of which scopes were used and a value for each scope.
    For example, the `"actions"` scope will contain a `"actions"` property which contains
    a list of supported action names.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> apiReflect(["actions", "invalidType"], ["apiReflect", "invalidMethod"])
    {"scopes": ["actions"], "actions": ["apiReflect"]}
    ```
    </details>

```python
def sync():
```
*   Synchronizes the local Anki collections with AnkiWeb.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> sync()
    None
    ```
    </details>

```python
def getProfiles():
```
*   Retrieve the list of profiles.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getProfiles()
    ["User 1"]
    ```
    </details>

```python
def loadProfile(name):
```
*   Selects the profile specified in request.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> loadProfile("user1")
    True
    ```
    </details>

```python
def multi(actions):
```
*   Performs multiple actions in one request, returning an array with the response of
    each action (in the given order).

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> multi(
    ...     [
    ...         {"action": "deckNames"},
    ...         {"action": "deckNames", "version": 6},
    ...         {"action": "invalidAction", "params": {"useless": "param"}},
    ...         {"action": "invalidAction", "params": {"useless": "param"}, "version": 6},
    ...     ]
    ... )
    [
        ["Default"],
        {"result": ["Default"], "error": None},
        {"result": None, "error": "unsupported action"},
        {"result": None, "error": "unsupported action"},
    ]
    ```
    </details>

```python
def exportPackage(deck, path, includeSched):
```
*   Exports a given deck in `.apkg` format. Returns `True` if successful or `False`
    otherwise. The optional property `includeSched` (default is `False`) can be specified
    to include the cards' scheduling data.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> exportPackage("Default", "/data/Deck.apkg", True)
    True
    ```
    </details>

```python
def importPackage(path):
```
*   Imports a file in `.apkg` format into the collection. Returns `True` if successful
    or `False` otherwise. Note that the file path is relative to Anki's collection.media
    folder, not to the client.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> importPackage("/data/Deck.apkg")
    True
    ```
    </details>

```python
def reloadCollection():
```
*   Tells anki to reload all data from the database.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> reloadCollection()
    None
    ```
    </details>

### Model Actions

```python
def modelNames():
```
*   Gets the complete list of model names for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelNames()
    ["Basic", "Basic (and reversed card)"]
    ```
    </details>

```python
def modelNamesAndIds():
```
*   Gets the complete list of model names and their corresponding IDs for the current
    user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelNamesAndIds()
    {
        "Basic": 1483883011648,
        "Basic (and reversed card)": 1483883011644,
        "Basic (optional reversed card)": 1483883011631,
        "Cloze": 1483883011630,
    }
    ```
    </details>

```python
def findModelsById(modelIds):
```
*   Gets a list of models  for the provided model IDs from the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> findModelsById([1704387367119, 1704387398570])
    [
        {
            "id": 1704387367119,
            "name": "Basic",
            "type": 0,
            "mod": 1704387367,
            "usn": -1,
            "sortf": 0,
            "did": None,
            "tmpls": [
                {
                    "name": "Card 1",
                    "ord": 0,
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                    "id": 9176047152973362695,
                }
            ],
            "flds": [
                {
                    "name": "Front",
                    "ord": 0,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": 2453723143453745216,
                    "tag": None,
                    "preventDeletion": False,
                },
                {
                    "name": "Back",
                    "ord": 1,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": -4853200230425436781,
                    "tag": None,
                    "preventDeletion": False,
                },
            ],
            "css": ".card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n",
            "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            "latexPost": "\\end{document}",
            "latexsvg": False,
            "req": [[0, "any", [0]]],
            "originalStockKind": 1,
        },
        {
            "id": 1704387398570,
            "name": "Basic (and reversed card)",
            "type": 0,
            "mod": 1704387398,
            "usn": -1,
            "sortf": 0,
            "did": None,
            "tmpls": [
                {
                    "name": "Card 1",
                    "ord": 0,
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                    "id": 1689886528158874152,
                },
                {
                    "name": "Card 2",
                    "ord": 1,
                    "qfmt": "{{Back}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                    "id": -7839609225644824587,
                },
            ],
            "flds": [
                {
                    "name": "Front",
                    "ord": 0,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": -7787837672455357996,
                    "tag": None,
                    "preventDeletion": False,
                },
                {
                    "name": "Back",
                    "ord": 1,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": 6364828289839985081,
                    "tag": None,
                    "preventDeletion": False,
                },
            ],
            "css": ".card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n",
            "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            "latexPost": "\\end{document}",
            "latexsvg": False,
            "req": [[0, "any", [0]], [1, "any", [1]]],
            "originalStockKind": 1,
        },
    ]
    ```
    </details>

```python
def findModelsByName(modelNames):
```
*   Gets a list of models for the provided model names from the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> findModelsByName(["Basic", "Basic (and reversed card)"])
    [
        {
            "id": 1704387367119,
            "name": "Basic",
            "type": 0,
            "mod": 1704387367,
            "usn": -1,
            "sortf": 0,
            "did": None,
            "tmpls": [
                {
                    "name": "Card 1",
                    "ord": 0,
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                    "id": 9176047152973362695,
                }
            ],
            "flds": [
                {
                    "name": "Front",
                    "ord": 0,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": 2453723143453745216,
                    "tag": None,
                    "preventDeletion": False,
                },
                {
                    "name": "Back",
                    "ord": 1,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": -4853200230425436781,
                    "tag": None,
                    "preventDeletion": False,
                },
            ],
            "css": ".card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n",
            "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            "latexPost": "\\end{document}",
            "latexsvg": False,
            "req": [[0, "any", [0]]],
            "originalStockKind": 1,
        },
        {
            "id": 1704387398570,
            "name": "Basic (and reversed card)",
            "type": 0,
            "mod": 1704387398,
            "usn": -1,
            "sortf": 0,
            "did": None,
            "tmpls": [
                {
                    "name": "Card 1",
                    "ord": 0,
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                    "id": 1689886528158874152,
                },
                {
                    "name": "Card 2",
                    "ord": 1,
                    "qfmt": "{{Back}}",
                    "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}",
                    "bqfmt": "",
                    "bafmt": "",
                    "did": None,
                    "bfont": "",
                    "bsize": 0,
                    "id": -7839609225644824587,
                },
            ],
            "flds": [
                {
                    "name": "Front",
                    "ord": 0,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": -7787837672455357996,
                    "tag": None,
                    "preventDeletion": False,
                },
                {
                    "name": "Back",
                    "ord": 1,
                    "sticky": False,
                    "rtl": False,
                    "font": "Arial",
                    "size": 20,
                    "description": "",
                    "plainText": False,
                    "collapsed": False,
                    "excludeFromSearch": False,
                    "id": 6364828289839985081,
                    "tag": None,
                    "preventDeletion": False,
                },
            ],
            "css": ".card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n",
            "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            "latexPost": "\\end{document}",
            "latexsvg": False,
            "req": [[0, "any", [0]], [1, "any", [1]]],
            "originalStockKind": 1,
        },
    ]
    ```
    </details>

```python
def modelFieldNames(modelName):
```
*   Gets the complete list of field names for the provided model name.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldNames("Basic")
    ["Front", "Back"]
    ```
    </details>

```python
def modelFieldDescriptions(modelName):
```
*   Gets the complete list of field descriptions (the text seen in the gui editor when
    a field is empty) for the provided model name.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldDescriptions("Basic")
    ["", ""]
    ```
    </details>

```python
def modelFieldFonts(modelName):
```
*   Gets the complete list of fonts along with their font sizes.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldFonts("Basic")
    {"Front": {"font": "Arial", "size": 20}, "Back": {"font": "Arial", "size": 20}}
    ```
    </details>

```python
def modelFieldsOnTemplates(modelName):
```
*   Returns an object indicating the fields on the question and answer side of each
    card template for the given model name. The question side is given first in each
    array.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldsOnTemplates("Basic (and reversed card)")
    {"Card 1": [["Front"], ["Back"]], "Card 2": [["Back"], ["Front"]]}
    ```
    </details>

```python
def createModel(modelName, inOrderFields, css, isCloze, cardTemplates):
```
*   Creates a new model to be used in Anki. User must provide the `modelName`,
    `inOrderFields` and `cardTemplates` to be used in the model. There are optional fields
    `css` and `isCloze`. If not specified, `css` will use the default Anki css and
    `isCloze` will be equal to `False`. If `isCloze` is `True` then model will be created
    as Cloze.

    Optionally the `Name` field can be provided for each entry of `cardTemplates`. By
    default the card names will be `Card 1`, `Card 2`, and so on.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> createModel(
    ...     "newModelName",
    ...     ["Field1", "Field2", "Field3"],
    ...     "Optional CSS with default to builtin css",
    ...     False,
    ...     [
    ...         {
    ...             "Name": "My Card 1",
    ...             "Front": "Front html {{Field1}}",
    ...             "Back": "Back html  {{Field2}}",
    ...         }
    ...     ],
    ... )
    {
        "sortf": 0,
        "did": 1,
        "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
        "latexPost": "\\end{document}",
        "mod": 1551462107,
        "usn": -1,
        "vers": [],
        "type": 0,
        "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n",
        "name": "TestApiModel",
        "flds": [
            {
                "name": "Field1",
                "ord": 0,
                "sticky": False,
                "rtl": False,
                "font": "Arial",
                "size": 20,
                "media": [],
            },
            {
                "name": "Field2",
                "ord": 1,
                "sticky": False,
                "rtl": False,
                "font": "Arial",
                "size": 20,
                "media": [],
            },
        ],
        "tmpls": [
            {
                "name": "My Card 1",
                "ord": 0,
                "qfmt": "",
                "afmt": "This is the back of the card {{Field2}}",
                "did": None,
                "bqfmt": "",
                "bafmt": "",
            }
        ],
        "tags": [],
        "id": 1551462107104,
        "req": [[0, "none", []]],
    }
    ```
    </details>

```python
def modelTemplates(modelName):
```
*   Returns an object indicating the template content for each card connected to the
    provided model by name.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelTemplates("Basic (and reversed card)")
    {
        "Card 1": {
            "Front": "{{Front}}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
        },
        "Card 2": {
            "Front": "{{Back}}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}",
        },
    }
    ```
    </details>

```python
def modelStyling(modelName):
```
*   Gets the CSS styling for the provided model by name.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelStyling("Basic (and reversed card)")
    {
        "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n"
    }
    ```
    </details>

```python
def updateModelTemplates(model):
```
*   Modify the templates of an existing model by name. Only specifies cards and
    specified sides will be modified. If an existing card or side is not included in the
    request, it will be left unchanged.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> updateModelTemplates(
    ...     {
    ...         "name": "Custom",
    ...         "templates": {"Card 1": {"Front": "{{Question}}?", "Back": "{{Answer}}!"}},
    ...     }
    ... )
    None
    ```
    </details>

```python
def updateModelStyling(model):
```
*   Modify the CSS styling of an existing model by name.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> updateModelStyling({"name": "Custom", "css": "p { color: blue; }"})
    None
    ```
    </details>

```python
def findAndReplaceInModels(model):
```
*   Find and replace string in existing model by model name. Customise to replace in
    front, back or css by setting to true/false.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> findAndReplaceInModels(
    ...     {
    ...         "modelName": "",
    ...         "findText": "text_to_replace",
    ...         "replaceText": "replace_with_text",
    ...         "front": True,
    ...         "back": True,
    ...         "css": True,
    ...     }
    ... )
    1
    ```
    </details>

```python
def modelTemplateRename(modelName, oldTemplateName, newTemplateName):
```
*   Renames a template in an existing model.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelTemplateRename("Basic", "Card 1", "Card 1 renamed")
    None
    ```
    </details>

```python
def modelTemplateReposition(modelName, templateName, index):
```
*   Repositions a template in an existing model.

    The value of `index` starts at 0. For example, an index of `0` puts the template in
    the first position, and an index of `2` puts the template in the third position.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelTemplateReposition("Basic", "Card 1", 1)
    None
    ```
    </details>

```python
def modelTemplateAdd(modelName, template):
```
*   Adds a template to an existing model by name. If you want to update an existing
    template, use `updateModelTemplates`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelTemplateAdd(
    ...     "Basic",
    ...     {
    ...         "Name": "Card 3",
    ...         "Front": "Front html {{Field1}}",
    ...         "Back": "Back html {{Field2}}",
    ...     },
    ... )
    None
    ```
    </details>

```python
def modelTemplateRemove(modelName, templateName):
```
*   Removes a template from an existing model.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelTemplateRemove("Basic", "Card 1")
    None
    ```
    </details>

```python
def modelFieldRename(modelName, oldFieldName, newFieldName):
```
*   Rename the field name of a given model.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldRename("Basic", "Front", "FrontRenamed")
    None
    ```
    </details>

```python
def modelFieldReposition(modelName, fieldName, index):
```
*   Reposition the field within the field list of a given model.

    The value of `index` starts at 0. For example, an index of `0` puts the field in the
    first position, and an index of `2` puts the field in the third position.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldReposition("Basic", "Back", 0)
    None
    ```
    </details>

```python
def modelFieldAdd(modelName, fieldName, index):
```
*   Creates a new field within a given model.

    Optionally, the `index` value can be provided, which works exactly the same as the
    index in `modelFieldReposition`. By default, the field is added to the end of the
    field list.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldAdd("Basic", "NewField", 0)
    None
    ```
    </details>

```python
def modelFieldRemove(modelName, fieldName):
```
*   Deletes a field within a given model.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldRemove("Basic", "Front")
    None
    ```
    </details>

```python
def modelFieldSetFont(modelName, fieldName, font):
```
*   Sets the font for a field within a given model.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldSetFont("Basic", "Front", "Courier")
    None
    ```
    </details>

```python
def modelFieldSetFontSize(modelName, fieldName, fontSize):
```
*   Sets the font size for a field within a given model.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldSetFontSize("Basic", "Front", 10)
    None
    ```
    </details>

```python
def modelFieldSetDescription(modelName, fieldName, description):
```
*   Sets the description (the text seen in the gui editor when a field is empty) for a
    field within a given model.

    Older versions of Anki (2.1.49 and below) do not have field descriptions. In that
    case, this will return with `False`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> modelFieldSetDescription("Basic", "Front", "example field description")
    True
    ```
    </details>

### Note Actions

```python
def addNote(note):
```
*   Creates a note using the given deck and model, with the provided field values and
    tags. Returns the identifier of the created note created on success, and `None` on
    failure.

    Anki-Connect can download audio, video, and picture files and embed them in newly
    created notes. The corresponding `audio`, `video`, and `picture` note members are
    optional and can be omitted. If you choose to include any of them, they should contain
    a single object or an array of objects with the mandatory `filename` field and one of
    `data`, `path` or `url`. Refer to the documentation of `storeMediaFile` for an
    explanation of these fields. The `skipHash` field can be optionally provided to skip
    the inclusion of files with an MD5 hash that matches the provided value. This is
    useful for avoiding the saving of error pages and stub files. The `fields` member is a
    list of fields that should play audio or video, or show a picture when the card is
    displayed in Anki. The `allowDuplicate` member inside `options` group can be set to
    true to enable adding duplicate cards. Normally duplicate cards can not be added and
    trigger exception.

    The `duplicateScope` member inside `options` can be used to specify the scope for
    which duplicates are checked. A value of `"deck"` will only check for duplicates in
    the target deck; any other value will check the entire collection.

    The `duplicateScopeOptions` object can be used to specify some additional settings:

    * `duplicateScopeOptions.deckName` will specify which deck to use for checking
    duplicates in. If undefined or `None`, the target deck will be used.
    * `duplicateScopeOptions.checkChildren` will change whether or not duplicate cards are
    checked in child decks. The default value is `False`.
    * `duplicateScopeOptions.checkAllModels` specifies whether duplicate checks are
    performed across all note types. The default value is `False`.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> addNote(
    ...     {
    ...         "deckName": "Default",
    ...         "modelName": "Basic",
    ...         "fields": {"Front": "front content", "Back": "back content"},
    ...         "options": {
    ...             "allowDuplicate": False,
    ...             "duplicateScope": "deck",
    ...             "duplicateScopeOptions": {
    ...                 "deckName": "Default",
    ...                 "checkChildren": False,
    ...                 "checkAllModels": False,
    ...             },
    ...         },
    ...         "tags": ["yomichan"],
    ...         "audio": [
    ...             {
    ...                 "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ",
    ...                 "filename": "yomichan_ねこ_猫.mp3",
    ...                 "skipHash": "7e2c2f954ef6051373ba916f000168dc",
    ...                 "fields": ["Front"],
    ...             }
    ...         ],
    ...         "video": [
    ...             {
    ...                 "url": "https://cdn.videvo.net/videvo_files/video/free/2015-06/small_watermarked/Contador_Glam_preview.mp4",
    ...                 "filename": "countdown.mp4",
    ...                 "skipHash": "4117e8aab0d37534d9c8eac362388bbe",
    ...                 "fields": ["Back"],
    ...             }
    ...         ],
    ...         "picture": [
    ...             {
    ...                 "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/A_black_cat_named_Tilly.jpg/220px-A_black_cat_named_Tilly.jpg",
    ...                 "filename": "black_cat.jpg",
    ...                 "skipHash": "8d6e4646dfae812bf39651b59d7429ce",
    ...                 "fields": ["Back"],
    ...             }
    ...         ],
    ...     }
    ... )
    1496198395707
    ```
    </details>

```python
def addNotes(notes):
```
*   Creates multiple notes using the given deck and model, with the provided field
    values and tags. Returns an array of identifiers of the created notes (notes that
    could not be created will have a `None` identifier). Please see the documentation for
    `addNote` for an explanation of objects in the `notes` array.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> addNotes(
    ...     [
    ...         {
    ...             "deckName": "Default",
    ...             "modelName": "Basic",
    ...             "fields": {"Front": "front content", "Back": "back content"},
    ...             "tags": ["yomichan"],
    ...             "audio": [
    ...                 {
    ...                     "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ",
    ...                     "filename": "yomichan_ねこ_猫.mp3",
    ...                     "skipHash": "7e2c2f954ef6051373ba916f000168dc",
    ...                     "fields": ["Front"],
    ...                 }
    ...             ],
    ...             "video": [
    ...                 {
    ...                     "url": "https://cdn.videvo.net/videvo_files/video/free/2015-06/small_watermarked/Contador_Glam_preview.mp4",
    ...                     "filename": "countdown.mp4",
    ...                     "skipHash": "4117e8aab0d37534d9c8eac362388bbe",
    ...                     "fields": ["Back"],
    ...                 }
    ...             ],
    ...             "picture": [
    ...                 {
    ...                     "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/A_black_cat_named_Tilly.jpg/220px-A_black_cat_named_Tilly.jpg",
    ...                     "filename": "black_cat.jpg",
    ...                     "skipHash": "8d6e4646dfae812bf39651b59d7429ce",
    ...                     "fields": ["Back"],
    ...                 }
    ...             ],
    ...         }
    ...     ]
    ... )
    [1496198395707, None]
    ```
    </details>

```python
def canAddNotes(notes):
```
*   Accepts an array of objects which define parameters for candidate notes (see
    `addNote`) and returns an array of booleans indicating whether or not the parameters
    at the corresponding index could be used to create a new note.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> canAddNotes(
    ...     [
    ...         {
    ...             "deckName": "Default",
    ...             "modelName": "Basic",
    ...             "fields": {"Front": "front content", "Back": "back content"},
    ...             "tags": ["yomichan"],
    ...         }
    ...     ]
    ... )
    [True]
    ```
    </details>

```python
def canAddNotesWithErrorDetail(notes):
```
*   Accepts an array of objects which define parameters for candidate notes (see
    `addNote`) and returns an array of objects with fields `canAdd` and `error`.

    * `canAdd` indicates whether or not the parameters at the corresponding index could be
    used to create a new note.
    * `error` contains an explanation of why a note cannot be added.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> canAddNotesWithErrorDetail(
    ...     [
    ...         {
    ...             "deckName": "Default",
    ...             "modelName": "Basic",
    ...             "fields": {"Front": "front content", "Back": "back content"},
    ...             "tags": ["yomichan"],
    ...         },
    ...         {
    ...             "deckName": "Default",
    ...             "modelName": "Basic",
    ...             "fields": {"Front": "front content 2", "Back": "back content 2"},
    ...             "tags": ["yomichan"],
    ...         },
    ...     ]
    ... )
    [
        {"canAdd": False, "error": "cannot create note because it is a duplicate"},
        {"canAdd": True},
    ]
    ```
    </details>

```python
def updateNoteFields(note):
```
*   Modify the fields of an existing note. You can also include audio, video, or
    picture files which will be added to the note with an optional `audio`, `video`, or
    `picture` property. Please see the documentation for `addNote` for an explanation of
    objects in the `audio`, `video`, or `picture` array.

    > **Warning**: You must not be viewing the note that you are updating on your Anki
    browser, otherwise the fields will not update. See [this
    issue](https://github.com/FooSoft/anki-connect/issues/82) for further details.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> updateNoteFields(
    ...     {
    ...         "id": 1514547547030,
    ...         "fields": {"Front": "new front content", "Back": "new back content"},
    ...         "audio": [
    ...             {
    ...                 "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ",
    ...                 "filename": "yomichan_ねこ_猫.mp3",
    ...                 "skipHash": "7e2c2f954ef6051373ba916f000168dc",
    ...                 "fields": ["Front"],
    ...             }
    ...         ],
    ...     }
    ... )
    None
    ```
    </details>

```python
def updateNote(note):
```
*   Modify the fields and/or tags of an existing note. In other words, combines
    `updateNoteFields` and `updateNoteTags`. Please see their documentation for an
    explanation of all properties.

    Either `fields` or `tags` property can be omitted without affecting the other. Thus
    valid requests to `updateNoteFields` also work with `updateNote`. The note must have
    the `fields` property in order to update the optional audio, video, or picture
    objects.

    If neither `fields` nor `tags` are provided, the method will fail. Fields are updated
    first and are not rolled back if updating tags fails. Tags are not updated if updating
    fields fails.

    > **Warning** You must not be viewing the note that you are updating on your Anki
    browser, otherwise the fields will not update. See [this
    issue](https://github.com/FooSoft/anki-connect/issues/82) for further details.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> updateNote(
    ...     {
    ...         "id": 1514547547030,
    ...         "fields": {"Front": "new front content", "Back": "new back content"},
    ...         "tags": ["new", "tags"],
    ...     }
    ... )
    None
    ```
    </details>

```python
def updateNoteTags(note, tags):
```
*   Set a note's tags by note ID. Old tags will be removed.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> updateNoteTags(1483959289817, ["european-languages"])
    None
    ```
    </details>

```python
def getNoteTags(note):
```
*   Get a note's tags by note ID.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getNoteTags(1483959289817)
    ["european-languages"]
    ```
    </details>

```python
def addTags(notes, tags):
```
*   Adds tags to notes by note ID.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> addTags([1483959289817, 1483959291695], "european-languages")
    None
    ```
    </details>

```python
def removeTags(notes, tags):
```
*   Remove tags from notes by note ID.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> removeTags([1483959289817, 1483959291695], "european-languages")
    None
    ```
    </details>

```python
def getTags():
```
*   Gets the complete list of tags for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getTags()
    ["european-languages", "idioms"]
    ```
    </details>

```python
def clearUnusedTags():
```
*   Clears all the unused tags in the notes for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> clearUnusedTags()
    None
    ```
    </details>

```python
def replaceTags(notes, tag_to_replace, replace_with_tag):
```
*   Replace tags in notes by note ID.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> replaceTags([1483959289817, 1483959291695], "european-languages", "french-languages")
    None
    ```
    </details>

```python
def replaceTagsInAllNotes(tag_to_replace, replace_with_tag):
```
*   Replace tags in all the notes for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> replaceTagsInAllNotes("european-languages", "french-languages")
    None
    ```
    </details>

```python
def findNotes(query):
```
*   Returns an array of note IDs for a given query. Query syntax is [documented
    here](https://docs.ankiweb.net/searching.html).

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> findNotes("deck:current")
    [1483959289817, 1483959291695]
    ```
    </details>

```python
def notesInfo(notes):
```
*   Returns a list of objects containing for each note ID the note fields, tags, note
    type and the cards belonging to the note.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> notesInfo([1502298033753])
    [
        {
            "noteId": 1502298033753,
            "modelName": "Basic",
            "tags": ["tag", "another_tag"],
            "fields": {
                "Front": {"value": "front content", "order": 0},
                "Back": {"value": "back content", "order": 1},
            },
        }
    ]
    ```
    </details>

```python
def deleteNotes(notes):
```
*   Deletes notes with the given ids. If a note has several cards associated with it,
    all associated cards will be deleted.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> deleteNotes([1502298033753])
    None
    ```
    </details>

```python
def removeEmptyNotes():
```
*   Removes all the empty notes for the current user.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> removeEmptyNotes()
    None
    ```
    </details>

### Statistic Actions

```python
def getNumCardsReviewedToday():
```
*   Gets the count of cards that have been reviewed in the current day (with day start
    time as configured by user in anki)

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getNumCardsReviewedToday()
    0
    ```
    </details>

```python
def getNumCardsReviewedByDay():
```
*   Gets the number of cards reviewed as a list of pairs of `(dateString, number)`

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getNumCardsReviewedByDay()
    [["2021-02-28", 124], ["2021-02-27", 261]]
    ```
    </details>

```python
def getCollectionStatsHTML(wholeCollection):
```
*   Gets the collection statistics report

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getCollectionStatsHTML(True)
    "<center> lots of HTML here </center>"
    ```
    </details>

```python
def cardReviews(deck, startID):
```
*   Requests all card reviews for a specified deck after a certain time. `startID` is
    the latest unix time not included in the result. Returns a list of 9-tuples
    `(reviewTime, cardID, usn, buttonPressed, newInterval, previousInterval, newFactor,
    reviewDuration, reviewType)`

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> cardReviews("default", 1594194095740)
    [
        [1594194095746, 1485369733217, -1, 3, 4, -60, 2500, 6157, 0],
        [1594201393292, 1485369902086, -1, 1, -60, -60, 0, 4846, 0],
    ]
    ```
    </details>

```python
def getReviewsOfCards(cards):
```
*   Requests all card reviews for each card ID. Returns a dictionary mapping each card
    ID to a list of dictionaries of the format:
    ```
    {
        "id": reviewTime,
        "usn": usn,
        "ease": buttonPressed,
        "ivl": newInterval,
        "lastIvl": previousInterval,
        "factor": newFactor,
        "time": reviewDuration,
        "type": reviewType,
    }
    ```
    The reason why these key values are used instead of the more descriptive counterparts
    is because these are the exact key values used in Anki's database.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getReviewsOfCards(["1653613948202"])
    {
        "1653613948202": [
            {
                "id": 1653772912146,
                "usn": 1750,
                "ease": 1,
                "ivl": -20,
                "lastIvl": -20,
                "factor": 0,
                "time": 38192,
                "type": 0,
            },
            {
                "id": 1653772965429,
                "usn": 1750,
                "ease": 3,
                "ivl": -45,
                "lastIvl": -20,
                "factor": 0,
                "time": 15337,
                "type": 0,
            },
        ]
    }
    ```
    </details>

```python
def getLatestReviewID(deck):
```
*   Returns the unix time of the latest review for the given deck. 0 if no review has
    ever been made for the deck.

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> getLatestReviewID("default")
    1594194095746
    ```
    </details>

```python
def insertReviews(reviews):
```
*   Inserts the given reviews into the database. Required format: list of 9-tuples
    `(reviewTime, cardID, usn, buttonPressed, newInterval, previousInterval, newFactor,
    reviewDuration, reviewType)`

    <details>
    <summary><i>Example:</i></summary>

    ```python
    >>> insertReviews(
    ...     [
    ...         [1594194095746, 1485369733217, -1, 3, 4, -60, 2500, 6157, 0],
    ...         [1594201393292, 1485369902086, -1, 1, -60, -60, 0, 4846, 0],
    ...     ]
    ... )
    None
    ```
    </details>

