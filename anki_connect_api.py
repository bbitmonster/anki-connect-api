__version__ = '24.2.26.0'

import json
import urllib.request

URL = 'http://127.0.0.1:8765'


def invoke(action: str, **params):
    requestJson = json.dumps({
        'action': action,
        'version': 6,
        'params': params
    }).encode('utf-8')
    response = json.load(
        urllib.request.urlopen(urllib.request.Request(URL, requestJson))
    )
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


# Card Actions

def getEaseFactors(cards: list) -> list:
    """Returns an array with the ease factor for each of the given cards (in the same
    order).

    Example::
        >>> getEaseFactors([1483959291685, 1483959293217])
        [4100, 3900]
    """
    return invoke("getEaseFactors", cards=cards)


def setEaseFactors(cards: list, easeFactors: list) -> list:
    """Sets ease factor of cards by card ID; returns `True` if successful (all cards
    existed) or `False` otherwise.

    Example::
        >>> setEaseFactors([1483959291685, 1483959293217], [4100, 3900])
        [True, True]
    """
    return invoke("setEaseFactors", cards=cards, easeFactors=easeFactors)


def setSpecificValueOfCard(card: int, keys: list, newValues: list) -> list:
    """Sets specific value of a single card. Given the risk of wreaking havor in the
    database when changing some of the values of a card, some of the keys require the
    argument "warning_check" set to True. This can be used to set a card's flag, change
    it's ease factor, change the review order in a filtered deck and change the column
    "data" (not currently used by anki apparantly), and many other values. A list of
    values and explanation of their respective utility can be found at [AnkiDroid's
    wiki](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure).

    Example::
        >>> setSpecificValueOfCard(1483959291685, ["flags", "odue"], ["1", "-100"])
        [True, True]
    """
    return invoke(
        "setSpecificValueOfCard", card=card, keys=keys, newValues=newValues
    )


def suspend(cards: list) -> bool:
    """Suspend cards by card ID; returns `True` if successful (at least one card wasn't
    already suspended) or `False` otherwise.

    Example::
        >>> suspend([1483959291685, 1483959293217])
        True
    """
    return invoke("suspend", cards=cards)


def unsuspend(cards: list) -> bool:
    """Unsuspend cards by card ID; returns `True` if successful (at least one card was
    previously suspended) or `False` otherwise.

    Example::
        >>> unsuspend([1483959291685, 1483959293217])
        True
    """
    return invoke("unsuspend", cards=cards)


def suspended(card: int) -> bool:
    """Check if card is suspended by its ID. Returns `True` if suspended, `False`
    otherwise.

    Example::
        >>> suspended(1483959293217)
        True
    """
    return invoke("suspended", card=card)


def areSuspended(cards: list) -> list:
    """Returns an array indicating whether each of the given cards is suspended (in the
    same order). If card doesn't exist returns `None`.

    Example::
        >>> areSuspended([1483959291685, 1483959293217, 1234567891234])
        [False, True, None]
    """
    return invoke("areSuspended", cards=cards)


def areDue(cards: list) -> list:
    """Returns an array indicating whether each of the given cards is due (in the same
    order). *Note*: cards in the learning queue with a large interval (over 20 minutes)
    are treated as not due until the time of their interval has passed, to match the way
    Anki treats them when reviewing.

    Example::
        >>> areDue([1483959291685, 1483959293217])
        [False, True]
    """
    return invoke("areDue", cards=cards)


def getIntervals(cards: list, complete: bool = False) -> list:
    """Returns an array of the most recent intervals for each given card ID, or a
    2-dimensional array of all the intervals for each given card ID when `complete` is
    `True`. Negative intervals are in seconds and positive intervals in days.

    Example::
        >>> getIntervals([1502298033753, 1502298036657])
        [-14400, 3]

        >>> getIntervals([1502298033753, 1502298036657], True)
        [
            [-120, -180, -240, -300, -360, -14400],
            [-120, -180, -240, -300, -360, -14400, 1, 3]
        ]
    """
    return invoke("getIntervals", cards=cards, complete=complete)


def findCards(query: str) -> list:
    """Returns an array of card IDs for a given query. Functionally identical to
    `guiBrowse` but doesn't use the GUI for better performance.

    Example::
        >>> findCards("deck:current")
        [1494723142483, 1494703460437, 1494703479525]
    """
    return invoke("findCards", query=query)


def cardsToNotes(cards: list) -> list:
    """Returns an unordered array of note IDs for the given card IDs. For cards with the
    same note, the ID is only given once in the array.

    Example::
        >>> cardsToNotes([1502098034045, 1502098034048, 1502298033753])
        [1502098029797, 1502298025183]
    """
    return invoke("cardsToNotes", cards=cards)


def cardsModTime(cards: list) -> list:
    """Returns a list of objects containings for each card ID the modification time. This
    function is about 15 times faster than executing `cardsInfo`.

    Example::
        >>> cardsModTime([1498938915662, 1502098034048])
        [{"cardId": 1498938915662, "mod": 1629454092}]
    """
    return invoke("cardsModTime", cards=cards)


def cardsInfo(cards: list) -> list:
    """Returns a list of objects containing for each card ID the card fields, front and
    back sides including CSS, note type, the note that the card belongs to, and deck name,
    last modification timestamp as well as ease and interval.

    Example::
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
    """
    return invoke("cardsInfo", cards=cards)


def forgetCards(cards: list) -> None:
    """Forget cards, making the cards new again.

    Example::
        >>> forgetCards([1498938915662, 1502098034048])
    """
    return invoke("forgetCards", cards=cards)


def relearnCards(cards: list) -> None:
    """Make cards be "relearning".

    Example::
        >>> relearnCards([1498938915662, 1502098034048])
    """
    return invoke("relearnCards", cards=cards)


def answerCards(answers: list) -> list:
    """Answer cards. Ease is between 1 (Again) and 4 (Easy). Will start the timer
    immediately before answering. Returns `True` if card exists, `False` otherwise.

    Example::
        >>> answerCards(
        ...     [{"cardId": 1498938915662, "ease": 2}, {"cardId": 1502098034048, "ease": 4}]
        ... )
        [True, True]
    """
    return invoke("answerCards", answers=answers)

# Deck Actions

def deckNames() -> list:
    """Gets the complete list of deck names for the current user.

    Example::
        >>> deckNames()
        ["Default"]
    """
    return invoke("deckNames")


def deckNamesAndIds() -> dict:
    """Gets the complete list of deck names and their respective IDs for the current user.

    Example::
        >>> deckNamesAndIds()
        {"Default": 1}
    """
    return invoke("deckNamesAndIds")


def getDecks(cards: list) -> dict:
    """Accepts an array of card IDs and returns an object with each deck name as a key,
    and its value an array of the given cards which belong to it.

    Example::
        >>> getDecks([1502298036657, 1502298033753, 1502032366472])
        {
            "Default": [1502032366472],
            "Japanese::JLPT N3": [1502298036657, 1502298033753],
        }
    """
    return invoke("getDecks", cards=cards)


def createDeck(deck: str) -> int:
    """Create a new empty deck. Will not overwrite a deck that exists with the same name.

    Example::
        >>> createDeck("Japanese::Tokyo")
        1519323742721
    """
    return invoke("createDeck", deck=deck)


def changeDeck(cards: list, deck: str) -> None:
    """Moves cards with the given IDs to a different deck, creating the deck if it doesn't
    exist yet.

    Example::
        >>> changeDeck([1502098034045, 1502098034048, 1502298033753], "Japanese::JLPT N3")
    """
    return invoke("changeDeck", cards=cards, deck=deck)


def deleteDecks(decks: list, cardsToo: bool) -> None:
    """Deletes decks with the given names. The argument `cardsToo` *must* be specified and
    set to `True`.

    Example::
        >>> deleteDecks(["Japanese::JLPT N5", "Easy Spanish"], True)
    """
    return invoke("deleteDecks", decks=decks, cardsToo=cardsToo)


def getDeckConfig(deck: str) -> dict:
    """Gets the configuration group object for the given deck.

    Example::
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
    """
    return invoke("getDeckConfig", deck=deck)


def saveDeckConfig(config: dict) -> bool:
    """Saves the given configuration group, returning `True` on success or `False` if the
    ID of the configuration group is invalid (such as when it does not exist).

    Example::
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
    """
    return invoke("saveDeckConfig", config=config)


def setDeckConfigId(decks: list, configId: int) -> bool:
    """Changes the configuration group for the given decks to the one with the given ID.
    Returns `True` on success or `False` if the given configuration group or any of the
    given decks do not exist.

    Example::
        >>> setDeckConfigId(["Default"], 1)
        True
    """
    return invoke("setDeckConfigId", decks=decks, configId=configId)


def cloneDeckConfigId(name: str, cloneFrom: int) -> int:
    """Creates a new configuration group with the given name, cloning from the group with
    the given ID, or from the default group if this is unspecified. Returns the ID of the
    new configuration group, or `False` if the specified group to clone from does not
    exist.

    Example::
        >>> cloneDeckConfigId("Copy of Default", 1)
        1502972374573
    """
    return invoke("cloneDeckConfigId", name=name, cloneFrom=cloneFrom)


def removeDeckConfigId(configId: int) -> bool:
    """Removes the configuration group with the given ID, returning `True` if successful,
    or `False` if attempting to remove either the default configuration group (ID = 1) or
    a configuration group that does not exist.

    Example::
        >>> removeDeckConfigId(1502972374573)
        True
    """
    return invoke("removeDeckConfigId", configId=configId)


def getDeckStats(decks: list) -> dict:
    """Gets statistics such as total cards and cards due for the given decks.

    Example::
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
    """
    return invoke("getDeckStats", decks=decks)

# Graphical Actions

def guiBrowse(query: str, reorderCards: dict) -> list:
    """Invokes the *Card Browser* dialog and searches for a given query. Returns an array
    of identifiers of the cards that were found. Query syntax is [documented
    here](https://docs.ankiweb.net/searching.html).

    Optionally, the `reorderCards` property can be provided to reorder the cards shown in
    the *Card Browser*. This is an array including the `order` and `columnId` objects.
    `order` can be either `ascending` or `descending` while `columnId` can be one of
    several column identifiers (as documented in the [Anki source
    code](https://github.com/ankitects/anki/blob/main/rslib/src/browser_table.rs)). The
    specified column needs to be visible in the *Card Browser*.

    Example::
        >>> guiBrowse("deck:current", {"order": "descending", "columnId": "noteCrt"})
        [1494723142483, 1494703460437, 1494703479525]
    """
    return invoke("guiBrowse", query=query, reorderCards=reorderCards)


def guiSelectNote(note: int) -> bool:
    """Finds the open instance of the *Card Browser* dialog and selects a note given a
    note identifier. Returns `True` if the *Card Browser* is open, `False` otherwise.

    Example::
        >>> guiSelectNote(1494723142483)
        True
    """
    return invoke("guiSelectNote", note=note)


def guiSelectedNotes() -> list:
    """Finds the open instance of the *Card Browser* dialog and returns an array of
    identifiers of the notes that are selected. Returns an empty list if the browser is
    not open.

    Example::
        >>> guiSelectedNotes()
        [1494723142483, 1494703460437, 1494703479525]
    """
    return invoke("guiSelectedNotes")


def guiAddCards(note: dict) -> int:
    """Invokes the *Add Cards* dialog, presets the note using the given deck and model,
    with the provided field values and tags. Invoking it multiple times closes the old
    window and _reopen the window_ with the new provided values.

    Audio, video, and picture files can be embedded into the fields via the `audio`,
    `video`, and `picture` keys, respectively. Refer to the documentation of `addNote` and
    `storeMediaFile` for an explanation of these fields.

    The result is the ID of the note which would be added, if the user chose to confirm
    the *Add Cards* dialogue.

    Example::
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
    """  # noqa: E501
    return invoke("guiAddCards", note=note)


def guiEditNote(note: int) -> None:
    """Opens the *Edit* dialog with a note corresponding to given note ID. The dialog is
    similar to the *Edit Current* dialog, but:

    * has a Preview button to preview the cards for the note
    * has a Browse button to open the browser with these cards
    * has Previous/Back buttons to navigate the history of the dialog
    * has no bar with the Close button

    Example::
        >>> guiEditNote(1649198355435)
    """
    return invoke("guiEditNote", note=note)


def guiCurrentCard() -> dict:
    """Returns information about the current card or `None` if not in review mode.

    Example::
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
    """
    return invoke("guiCurrentCard")


def guiStartCardTimer() -> bool:
    """Starts or resets the `timerStarted` value for the current card. This is useful for
    deferring the start time to when it is displayed via the API, allowing the recorded
    time taken to answer the card to be more accurate when calling `guiAnswerCard`.

    Example::
        >>> guiStartCardTimer()
        True
    """
    return invoke("guiStartCardTimer")


def guiShowQuestion() -> bool:
    """Shows question text for the current card; returns `True` if in review mode or
    `False` otherwise.

    Example::
        >>> guiShowQuestion()
        True
    """
    return invoke("guiShowQuestion")


def guiShowAnswer() -> bool:
    """Shows answer text for the current card; returns `True` if in review mode or `False`
    otherwise.

    Example::
        >>> guiShowAnswer()
        True
    """
    return invoke("guiShowAnswer")


def guiAnswerCard(ease: int) -> bool:
    """Answers the current card; returns `True` if succeeded or `False` otherwise. Note
    that the answer for the current card must be displayed before before any answer can be
    accepted by Anki.

    Example::
        >>> guiAnswerCard(1)
        True
    """
    return invoke("guiAnswerCard", ease=ease)


def guiUndo() -> bool:
    """Undo the last action / card; returns `True` if succeeded or `False` otherwise.

    Example::
        >>> guiUndo()
        True
    """
    return invoke("guiUndo")


def guiDeckOverview(name: str) -> bool:
    """Opens the *Deck Overview* dialog for the deck with the given name; returns `True`
    if succeeded or `False` otherwise.

    Example::
        >>> guiDeckOverview("Default")
        True
    """
    return invoke("guiDeckOverview", name=name)


def guiDeckBrowser() -> None:
    """Opens the *Deck Browser* dialog.

    Example::
        >>> guiDeckBrowser()
    """
    return invoke("guiDeckBrowser")


def guiDeckReview(name: str) -> bool:
    """Starts review for the deck with the given name; returns `True` if succeeded or
    `False` otherwise.

    Example::
        >>> guiDeckReview("Default")
        True
    """
    return invoke("guiDeckReview", name=name)


def guiImportFile(path: str) -> None:
    """Invokes the *Import... (Ctrl+Shift+I)* dialog with an optional file path. Brings up
    the dialog for user to review the import. Supports all file types that Anki supports.
    Brings open file dialog if no path is provided. Forward slashes must be used in the
    path on Windows. Only supported for Anki 2.1.52+.

    Example::
        >>> guiImportFile("C:/Users/Desktop/cards.txt")
    """
    return invoke("guiImportFile", path=path)


def guiExitAnki() -> None:
    """Schedules a request to gracefully close Anki. This operation is asynchronous, so it
    will return immediately and won't wait until the Anki process actually terminates.

    Example::
        >>> guiExitAnki()
    """
    return invoke("guiExitAnki")


def guiCheckDatabase() -> bool:
    """Requests a database check, but returns immediately without waiting for the check to
    complete. Therefore, the action will always return `True` even if errors are detected
    during the database check.

    Example::
        >>> guiCheckDatabase()
        True
    """
    return invoke("guiCheckDatabase")

# Media Actions

def storeMediaFile(
    filename: str,
    *,
    data: str = None,
    path: str = None,
    url: str = None,
    deleteExisting: bool = True
) -> str:
    """Stores a file with the specified base64-encoded contents inside the media folder.
    Alternatively you can specify a absolute file path, or a url from where the file shell
    be downloaded. If more than one of `data`, `path` and `url` are provided, the `data`
    field will be used first, then `path`, and finally `url`. To prevent Anki from
    removing files not used by any cards (e.g. for configuration files), prefix the
    filename with an underscore. These files are still synchronized to AnkiWeb. Any
    existing file with the same name is deleted by default. Set `deleteExisting` to false
    to prevent that by [letting Anki give the new file a non-conflicting
    name](https://github.com/ankitects/anki/blob/aeba725d3ea9628c73300648f748140db3fdd5ed/rslib/src/media/files.rs#L194).

    Example::
        >>> storeMediaFile("_hello.txt", data="SGVsbG8sIHdvcmxkIQ==")
        "_hello.txt"

        >>> storeMediaFile("_hello.txt", path="/path/to/file")
        "_hello.txt"

        >>> storeMediaFile("_hello.txt", url="https://url.to.file")
        "_hello.txt"
    """
    if data is not None:
        return invoke(
            "storeMediaFile",
            filename=filename,
            data=data,
            deleteExisting=deleteExisting,
        )
    elif path is not None:
        return invoke(
            "storeMediaFile",
            filename=filename,
            path=str(path),
            deleteExisting=deleteExisting,
        )
    elif url is not None:
        return invoke(
            "storeMediaFile",
            filename=filename,
            url=url,
            deleteExisting=deleteExisting,
        )
    else:
        raise Exception("one argument of data, path or url must be supplied")


def retrieveMediaFile(filename: str) -> str:
    """Retrieves the base64-encoded contents of the specified file, returning `False` if
    the file does not exist.

    Example::
        >>> retrieveMediaFile("_hello.txt")
        "SGVsbG8sIHdvcmxkIQ=="
    """
    return invoke("retrieveMediaFile", filename=filename)


def getMediaFilesNames(pattern: str) -> list:
    """Gets the names of media files matched the pattern. Returning all names by default.

    Example::
        >>> getMediaFilesNames("_hell*.txt")
        ["_hello.txt"]
    """
    return invoke("getMediaFilesNames", pattern=pattern)


def getMediaDirPath() -> str:
    """Gets the full path to the `collection.media` folder of the currently opened
    profile.

    Example::
        >>> getMediaDirPath()
        "/home/user/.local/share/Anki2/Main/collection.media"
    """
    return invoke("getMediaDirPath")


def deleteMediaFile(filename: str) -> None:
    """Deletes the specified file inside the media folder.

    Example::
        >>> deleteMediaFile("_hello.txt")
    """
    return invoke("deleteMediaFile", filename=filename)

# Miscellaneous Actions

def requestPermission() -> dict:
    """Requests permission to use the API exposed by this plugin. This method does not
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

    Example::
        >>> requestPermission()
        {"permission": "granted", "requireApiKey": False, "version": 6}
    """
    return invoke("requestPermission")


def version() -> int:
    """Gets the version of the API exposed by this plugin. Currently versions `1` through
    `6` are defined.

    Example::
        >>> version()
        6
    """
    return invoke("version")


def apiReflect(scopes: list, actions: list) -> dict:
    """Gets information about the AnkiConnect APIs available. The request supports the
    following params:

    * `scopes` - An array of scopes to get reflection information about. The only
    currently supported value is `"actions"`.
    * `actions` - Either `None` or an array of API method names to check for. If the value
    is `None`, the result will list all of the available API actions. If the value is an
    array of strings, the result will only contain actions which were in this array.

    The result will contain a list of which scopes were used and a value for each scope.
    For example, the `"actions"` scope will contain a `"actions"` property which contains
    a list of supported action names.

    Example::
        >>> apiReflect(["actions", "invalidType"], ["apiReflect", "invalidMethod"])
        {"scopes": ["actions"], "actions": ["apiReflect"]}
    """
    return invoke("apiReflect", scopes=scopes, actions=actions)


def sync() -> None:
    """Synchronizes the local Anki collections with AnkiWeb.

    Example::
        >>> sync()
    """
    return invoke("sync")


def getProfiles() -> list:
    """Retrieve the list of profiles.

    Example::
        >>> getProfiles()
        ["User 1"]
    """
    return invoke("getProfiles")


def loadProfile(name: str) -> bool:
    """Selects the profile specified in request.

    Example::
        >>> loadProfile("user1")
        True
    """
    return invoke("loadProfile", name=name)


def multi(actions: list) -> list:
    """Performs multiple actions in one request, returning an array with the response of
    each action (in the given order).

    Example::
        >>> multi(
        ...     [
        ...         {"action": "deckNames"},
        ...         {"action": "deckNames", "version": 6},
        ...         {"action": "invalidAction", "params": {"useless": "param"}},
        ...         {
        ...             "action": "invalidAction",
        ...             "params": {"useless": "param"},
        ...             "version": 6,
        ...         },
        ...     ]
        ... )
        [
            ["Default"],
            {"result": ["Default"], "error": None},
            {"result": None, "error": "unsupported action"},
            {"result": None, "error": "unsupported action"},
        ]
    """
    return invoke("multi", actions=actions)


def exportPackage(deck: str, path: str, includeSched: bool) -> bool:
    """Exports a given deck in `.apkg` format. Returns `True` if successful or `False`
    otherwise. The optional property `includeSched` (default is `False`) can be specified
    to include the cards' scheduling data.

    Example::
        >>> exportPackage("Default", "/data/Deck.apkg", True)
        True
    """
    return invoke(
        "exportPackage", deck=deck, path=path, includeSched=includeSched
    )


def importPackage(path: str) -> bool:
    """Imports a file in `.apkg` format into the collection. Returns `True` if successful
    or `False` otherwise. Note that the file path is relative to Anki's collection.media
    folder, not to the client.

    Example::
        >>> importPackage("/data/Deck.apkg")
        True
    """
    return invoke("importPackage", path=path)


def reloadCollection() -> None:
    """Tells anki to reload all data from the database.

    Example::
        >>> reloadCollection()
    """
    return invoke("reloadCollection")

# Model Actions

def modelNames() -> list:
    """Gets the complete list of model names for the current user.

    Example::
        >>> modelNames()
        ["Basic", "Basic (and reversed card)"]
    """
    return invoke("modelNames")


def modelNamesAndIds() -> dict:
    """Gets the complete list of model names and their corresponding IDs for the current
    user.

    Example::
        >>> modelNamesAndIds()
        {
            "Basic": 1483883011648,
            "Basic (and reversed card)": 1483883011644,
            "Basic (optional reversed card)": 1483883011631,
            "Cloze": 1483883011630,
        }
    """
    return invoke("modelNamesAndIds")


def findModelsById(modelIds: list) -> list:
    r"""Gets a list of models  for the provided model IDs from the current user.

    Example::
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
    """  # noqa: E501
    return invoke("findModelsById", modelIds=modelIds)


def findModelsByName(modelNames: list) -> list:
    r"""Gets a list of models for the provided model names from the current user.

    Example::
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
    """  # noqa: E501
    return invoke("findModelsByName", modelNames=modelNames)


def modelFieldNames(modelName: str) -> list:
    """Gets the complete list of field names for the provided model name.

    Example::
        >>> modelFieldNames("Basic")
        ["Front", "Back"]
    """
    return invoke("modelFieldNames", modelName=modelName)


def modelFieldDescriptions(modelName: str) -> list:
    """Gets the complete list of field descriptions (the text seen in the gui editor when
    a field is empty) for the provided model name.

    Example::
        >>> modelFieldDescriptions("Basic")
        ["", ""]
    """
    return invoke("modelFieldDescriptions", modelName=modelName)


def modelFieldFonts(modelName: str) -> dict:
    """Gets the complete list of fonts along with their font sizes.

    Example::
        >>> modelFieldFonts("Basic")
        {"Front": {"font": "Arial", "size": 20}, "Back": {"font": "Arial", "size": 20}}
    """
    return invoke("modelFieldFonts", modelName=modelName)


def modelFieldsOnTemplates(modelName: str) -> dict:
    """Returns an object indicating the fields on the question and answer side of each
    card template for the given model name. The question side is given first in each
    array.

    Example::
        >>> modelFieldsOnTemplates("Basic (and reversed card)")
        {"Card 1": [["Front"], ["Back"]], "Card 2": [["Back"], ["Front"]]}
    """
    return invoke("modelFieldsOnTemplates", modelName=modelName)


def createModel(
    modelName: str,
    inOrderFields: list,
    css: str,
    isCloze: bool,
    cardTemplates: list,
) -> dict:
    r"""Creates a new model to be used in Anki. User must provide the `modelName`,
    `inOrderFields` and `cardTemplates` to be used in the model. There are optional fields
    `css` and `isCloze`. If not specified, `css` will use the default Anki css and
    `isCloze` will be equal to `False`. If `isCloze` is `True` then model will be created
    as Cloze.

    Optionally the `Name` field can be provided for each entry of `cardTemplates`. By
    default the card names will be `Card 1`, `Card 2`, and so on.

    Example::
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
    """  # noqa: E501
    return invoke(
        "createModel",
        modelName=modelName,
        inOrderFields=inOrderFields,
        css=css,
        isCloze=isCloze,
        cardTemplates=cardTemplates,
    )


def modelTemplates(modelName: str) -> dict:
    r"""Returns an object indicating the template content for each card connected to the
    provided model by name.

    Example::
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
    """
    return invoke("modelTemplates", modelName=modelName)


def modelStyling(modelName: str) -> dict:
    r"""Gets the CSS styling for the provided model by name.

    Example::
        >>> modelStyling("Basic (and reversed card)")
        {
            "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n"
        }
    """  # noqa: E501
    return invoke("modelStyling", modelName=modelName)


def updateModelTemplates(model: dict) -> None:
    """Modify the templates of an existing model by name. Only specifies cards and
    specified sides will be modified. If an existing card or side is not included in the
    request, it will be left unchanged.

    Example::
        >>> updateModelTemplates(
        ...     {
        ...         "name": "Custom",
        ...         "templates": {
        ...             "Card 1": {"Front": "{{Question}}?", "Back": "{{Answer}}!"}
        ...         },
        ...     }
        ... )
    """
    return invoke("updateModelTemplates", model=model)


def updateModelStyling(model: dict) -> None:
    """Modify the CSS styling of an existing model by name.

    Example::
        >>> updateModelStyling({"name": "Custom", "css": "p { color: blue; }"})
    """
    return invoke("updateModelStyling", model=model)


def findAndReplaceInModels(model: dict) -> int:
    """Find and replace string in existing model by model name. Customise to replace in
    front, back or css by setting to true/false.

    Example::
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
    """
    return invoke("findAndReplaceInModels", model=model)


def modelTemplateRename(
    modelName: str, oldTemplateName: str, newTemplateName: str
) -> None:
    """Renames a template in an existing model.

    Example::
        >>> modelTemplateRename("Basic", "Card 1", "Card 1 renamed")
    """
    return invoke(
        "modelTemplateRename",
        modelName=modelName,
        oldTemplateName=oldTemplateName,
        newTemplateName=newTemplateName,
    )


def modelTemplateReposition(
    modelName: str, templateName: str, index: int
) -> None:
    """Repositions a template in an existing model.

    The value of `index` starts at 0. For example, an index of `0` puts the template in
    the first position, and an index of `2` puts the template in the third position.

    Example::
        >>> modelTemplateReposition("Basic", "Card 1", 1)
    """
    return invoke(
        "modelTemplateReposition",
        modelName=modelName,
        templateName=templateName,
        index=index,
    )


def modelTemplateAdd(modelName: str, template: dict) -> None:
    """Adds a template to an existing model by name. If you want to update an existing
    template, use `updateModelTemplates`.

    Example::
        >>> modelTemplateAdd(
        ...     "Basic",
        ...     {
        ...         "Name": "Card 3",
        ...         "Front": "Front html {{Field1}}",
        ...         "Back": "Back html {{Field2}}",
        ...     },
        ... )
    """
    return invoke("modelTemplateAdd", modelName=modelName, template=template)


def modelTemplateRemove(modelName: str, templateName: str) -> None:
    """Removes a template from an existing model.

    Example::
        >>> modelTemplateRemove("Basic", "Card 1")
    """
    return invoke(
        "modelTemplateRemove", modelName=modelName, templateName=templateName
    )


def modelFieldRename(
    modelName: str, oldFieldName: str, newFieldName: str
) -> None:
    """Rename the field name of a given model.

    Example::
        >>> modelFieldRename("Basic", "Front", "FrontRenamed")
    """
    return invoke(
        "modelFieldRename",
        modelName=modelName,
        oldFieldName=oldFieldName,
        newFieldName=newFieldName,
    )


def modelFieldReposition(modelName: str, fieldName: str, index: int) -> None:
    """Reposition the field within the field list of a given model.

    The value of `index` starts at 0. For example, an index of `0` puts the field in the
    first position, and an index of `2` puts the field in the third position.

    Example::
        >>> modelFieldReposition("Basic", "Back", 0)
    """
    return invoke(
        "modelFieldReposition",
        modelName=modelName,
        fieldName=fieldName,
        index=index,
    )


def modelFieldAdd(modelName: str, fieldName: str, index: int) -> None:
    """Creates a new field within a given model.

    Optionally, the `index` value can be provided, which works exactly the same as the
    index in `modelFieldReposition`. By default, the field is added to the end of the
    field list.

    Example::
        >>> modelFieldAdd("Basic", "NewField", 0)
    """
    return invoke(
        "modelFieldAdd", modelName=modelName, fieldName=fieldName, index=index
    )


def modelFieldRemove(modelName: str, fieldName: str) -> None:
    """Deletes a field within a given model.

    Example::
        >>> modelFieldRemove("Basic", "Front")
    """
    return invoke("modelFieldRemove", modelName=modelName, fieldName=fieldName)


def modelFieldSetFont(modelName: str, fieldName: str, font: str) -> None:
    """Sets the font for a field within a given model.

    Example::
        >>> modelFieldSetFont("Basic", "Front", "Courier")
    """
    return invoke(
        "modelFieldSetFont", modelName=modelName, fieldName=fieldName, font=font
    )


def modelFieldSetFontSize(
    modelName: str, fieldName: str, fontSize: int
) -> None:
    """Sets the font size for a field within a given model.

    Example::
        >>> modelFieldSetFontSize("Basic", "Front", 10)
    """
    return invoke(
        "modelFieldSetFontSize",
        modelName=modelName,
        fieldName=fieldName,
        fontSize=fontSize,
    )


def modelFieldSetDescription(
    modelName: str, fieldName: str, description: str
) -> bool:
    """Sets the description (the text seen in the gui editor when a field is empty) for a
    field within a given model.

    Older versions of Anki (2.1.49 and below) do not have field descriptions. In that
    case, this will return with `False`.

    Example::
        >>> modelFieldSetDescription("Basic", "Front", "example field description")
        True
    """
    return invoke(
        "modelFieldSetDescription",
        modelName=modelName,
        fieldName=fieldName,
        description=description,
    )

# Note Actions

def addNote(note: dict) -> int:
    """Creates a note using the given deck and model, with the provided field values and
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

    Example::
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
    """  # noqa: E501
    return invoke("addNote", note=note)


def addNotes(notes: list) -> list:
    """Creates multiple notes using the given deck and model, with the provided field
    values and tags. Returns an array of identifiers of the created notes (notes that
    could not be created will have a `None` identifier). Please see the documentation for
    `addNote` for an explanation of objects in the `notes` array.

    Example::
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
    """  # noqa: E501
    return invoke("addNotes", notes=notes)


def canAddNotes(notes: list) -> list:
    """Accepts an array of objects which define parameters for candidate notes (see
    `addNote`) and returns an array of booleans indicating whether or not the parameters
    at the corresponding index could be used to create a new note.

    Example::
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
    """
    return invoke("canAddNotes", notes=notes)


def canAddNotesWithErrorDetail(notes: list) -> list:
    """Accepts an array of objects which define parameters for candidate notes (see
    `addNote`) and returns an array of objects with fields `canAdd` and `error`.

    * `canAdd` indicates whether or not the parameters at the corresponding index could be
    used to create a new note.
    * `error` contains an explanation of why a note cannot be added.

    Example::
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
    """
    return invoke("canAddNotesWithErrorDetail", notes=notes)


def updateNoteFields(note: dict) -> None:
    """Modify the fields of an existing note. You can also include audio, video, or
    picture files which will be added to the note with an optional `audio`, `video`, or
    `picture` property. Please see the documentation for `addNote` for an explanation of
    objects in the `audio`, `video`, or `picture` array.

    > **Warning**: You must not be viewing the note that you are updating on your Anki
    browser, otherwise the fields will not update. See [this
    issue](https://github.com/FooSoft/anki-connect/issues/82) for further details.

    Example::
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
    """  # noqa: E501
    return invoke("updateNoteFields", note=note)


def updateNote(note: dict) -> None:
    """Modify the fields and/or tags of an existing note. In other words, combines
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

    Example::
        >>> updateNote(
        ...     {
        ...         "id": 1514547547030,
        ...         "fields": {"Front": "new front content", "Back": "new back content"},
        ...         "tags": ["new", "tags"],
        ...     }
        ... )
    """
    return invoke("updateNote", note=note)


def updateNoteTags(note: int, tags: list) -> None:
    """Set a note's tags by note ID. Old tags will be removed.

    Example::
        >>> updateNoteTags(1483959289817, ["european-languages"])
    """
    return invoke("updateNoteTags", note=note, tags=tags)


def getNoteTags(note: int) -> list:
    """Get a note's tags by note ID.

    Example::
        >>> getNoteTags(1483959289817)
        ["european-languages"]
    """
    return invoke("getNoteTags", note=note)


def addTags(notes: list, tags: str) -> None:
    """Adds tags to notes by note ID.

    Example::
        >>> addTags([1483959289817, 1483959291695], "european-languages")
    """
    return invoke("addTags", notes=notes, tags=tags)


def removeTags(notes: list, tags: str) -> None:
    """Remove tags from notes by note ID.

    Example::
        >>> removeTags([1483959289817, 1483959291695], "european-languages")
    """
    return invoke("removeTags", notes=notes, tags=tags)


def getTags() -> list:
    """Gets the complete list of tags for the current user.

    Example::
        >>> getTags()
        ["european-languages", "idioms"]
    """
    return invoke("getTags")


def clearUnusedTags() -> None:
    """Clears all the unused tags in the notes for the current user.

    Example::
        >>> clearUnusedTags()
    """
    return invoke("clearUnusedTags")


def replaceTags(
    notes: list, tag_to_replace: str, replace_with_tag: str
) -> None:
    """Replace tags in notes by note ID.

    Example::
        >>> replaceTags(
        ...     [1483959289817, 1483959291695], "european-languages", "french-languages"
        ... )
    """
    return invoke(
        "replaceTags",
        notes=notes,
        tag_to_replace=tag_to_replace,
        replace_with_tag=replace_with_tag,
    )


def replaceTagsInAllNotes(tag_to_replace: str, replace_with_tag: str) -> None:
    """Replace tags in all the notes for the current user.

    Example::
        >>> replaceTagsInAllNotes("european-languages", "french-languages")
    """
    return invoke(
        "replaceTagsInAllNotes",
        tag_to_replace=tag_to_replace,
        replace_with_tag=replace_with_tag,
    )


def findNotes(query: str) -> list:
    """Returns an array of note IDs for a given query. Query syntax is [documented
    here](https://docs.ankiweb.net/searching.html).

    Example::
        >>> findNotes("deck:current")
        [1483959289817, 1483959291695]
    """
    return invoke("findNotes", query=query)


def notesInfo(notes: list) -> list:
    """Returns a list of objects containing for each note ID the note fields, tags, note
    type and the cards belonging to the note.

    Example::
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
    """
    return invoke("notesInfo", notes=notes)


def deleteNotes(notes: list) -> None:
    """Deletes notes with the given ids. If a note has several cards associated with it,
    all associated cards will be deleted.

    Example::
        >>> deleteNotes([1502298033753])
    """
    return invoke("deleteNotes", notes=notes)


def removeEmptyNotes() -> None:
    """Removes all the empty notes for the current user.

    Example::
        >>> removeEmptyNotes()
    """
    return invoke("removeEmptyNotes")

# Statistic Actions

def getNumCardsReviewedToday() -> int:
    """Gets the count of cards that have been reviewed in the current day (with day start
    time as configured by user in anki)

    Example::
        >>> getNumCardsReviewedToday()
        0
    """
    return invoke("getNumCardsReviewedToday")


def getNumCardsReviewedByDay() -> list:
    """Gets the number of cards reviewed as a list of pairs of `(dateString, number)`

    Example::
        >>> getNumCardsReviewedByDay()
        [["2021-02-28", 124], ["2021-02-27", 261]]
    """
    return invoke("getNumCardsReviewedByDay")


def getCollectionStatsHTML(wholeCollection: bool) -> str:
    """Gets the collection statistics report

    Example::
        >>> getCollectionStatsHTML(True)
        "<center> lots of HTML here </center>"
    """
    return invoke("getCollectionStatsHTML", wholeCollection=wholeCollection)


def cardReviews(deck: str, startID: int) -> list:
    """Requests all card reviews for a specified deck after a certain time. `startID` is
    the latest unix time not included in the result. Returns a list of 9-tuples
    `(reviewTime, cardID, usn, buttonPressed, newInterval, previousInterval, newFactor,
    reviewDuration, reviewType)`

    Example::
        >>> cardReviews("default", 1594194095740)
        [
            [1594194095746, 1485369733217, -1, 3, 4, -60, 2500, 6157, 0],
            [1594201393292, 1485369902086, -1, 1, -60, -60, 0, 4846, 0],
        ]
    """
    return invoke("cardReviews", deck=deck, startID=startID)


def getReviewsOfCards(cards: list) -> dict:
    """Requests all card reviews for each card ID. Returns a dictionary mapping each card
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

    Example::
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
    """
    return invoke("getReviewsOfCards", cards=cards)


def getLatestReviewID(deck: str) -> int:
    """Returns the unix time of the latest review for the given deck. 0 if no review has
    ever been made for the deck.

    Example::
        >>> getLatestReviewID("default")
        1594194095746
    """
    return invoke("getLatestReviewID", deck=deck)


def insertReviews(reviews: list) -> None:
    """Inserts the given reviews into the database. Required format: list of 9-tuples
    `(reviewTime, cardID, usn, buttonPressed, newInterval, previousInterval, newFactor,
    reviewDuration, reviewType)`

    Example::
        >>> insertReviews(
        ...     [
        ...         [1594194095746, 1485369733217, -1, 3, 4, -60, 2500, 6157, 0],
        ...         [1594201393292, 1485369902086, -1, 1, -60, -60, 0, 4846, 0],
        ...     ]
        ... )
    """
    return invoke("insertReviews", reviews=reviews)
