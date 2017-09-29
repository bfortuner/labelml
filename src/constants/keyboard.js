
let buildKeymap = function() {
    console.log("building keymap");
    let map = {};
    for (let k of KEYS) {
        console.log(k)
        map[k.code] = k;
    }
    return map;
}

const KEYS = [
    {
        'key': 'tab',
        'code': 9,
        'combo': false,
        'desc': 'navigate right'
    },
    {
        'key': 'ctrl',
        'code': 17,
        'combo': false,
        'desc': null
    },
    {
        'key': 'shift',
        'code': 16,
        'combo': false,
        'desc': null
    },
    {
        'key': 'alt',
        'code': 18,
        'combo': false,
        'desc': null
    },
    {
        'key': 'meta',
        'code': 91,
        'combo': false,
        'desc': null
    },
    {
        'key': 'shift + tab',
        'code': null,
        'combo': true,
        'desc': 'navigate left'
    },
    {
        'key': 'ctrl + s',
        'code': null,
        'combo': true,
        'desc': 'save annotations'
    },
    {
        'key': 'delete',
        'code': 46,
        'combo': false,
        'desc': 'delete object'
    },
    {
        'key': 'backspace',
        'code': 8,
        'combo': false,
        'desc': 'delete object'
    },
    {
        'key': 'esc',
        'code': 27,
        'combo': false,
        'desc': 'deselect object'
    },
    {
        'key': 's',
        'code': 83,
        'combo': false,
        'desc': 'select mode'
    },
    {
        'key': 'd',
        'code': 68,
        'combo': false,
        'desc': 'draw mode'
    },
    {
        'key': 'c',
        'code': 67,
        'combo': false,
        'desc': 'click-to-box mode'
    },
    {
        'key': 'p',
        'code': 80,
        'combo': false,
        'desc': 'polygon mode'
    },
    {
        'key': 'n',
        'code': 78,
        'combo': false,
        'desc': 'next image'
    },
    {
        'key': 'z',
        'code': 90,
        'combo': false,
        'desc': 'zoom-in'
    },
    {
        'key': 'shift + z',
        'code': null,
        'combo': true,
        'desc': 'zoom-out'
    },
    {
        'key': 'h',
        'code': 72,
        'combo': false,
        'desc': 'hide/unhide non-selected'
    },
    {
        'key': 'up',
        'code': 38,
        'combo': false,
        'desc': 'move up'
    },
    {
        'key': 'down',
        'code': 40,
        'combo': false,
        'desc': 'move down'
    },
    {
        'key': 'left',
        'code': 37,
        'combo': false,
        'desc': 'move left'
    },
    {
        'key': 'right',
        'code': 39,
        'combo': false,
        'desc': 'move right'
    },
    {
        'key': 'wheelUp',
        'code': null,
        'combo': false,
        'desc': 'zoom-in'
    },
    {
        'key': 'wheelDown',
        'code': null,
        'combo': false,
        'desc': 'zoom-out'
    },
    {
        'key': 'click + drag',
        'code': null,
        'combo': true,
        'desc': 'pan (select mode only)'
    },
]

const KEY_MAP = buildKeymap()

const keys = {
    KEYS: KEYS,
    KEY_MAP: KEY_MAP
}

export default keys;