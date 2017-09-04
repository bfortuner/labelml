<template>
  <div class="editor">
    <button @click="getPrevImg()">Prev</button>
    <button @click="getNextImg()">Next</button>
    <button @click="save()">Save</button>
    <button @click="deleteObject()">Delete</button>
    <button @click="drawMode()">Draw</button>
    <button @click="selectMode()">Select</button>
    <select id='select-label' v-model="selectedLabel">
      <option v-for="label in labels" 
            v-bind:value="label.value" :key="label.value">
        {{ label.value }}
      </option>
    </select>
    <canvas id="c"></canvas>
  </div>
</template>

<script>
import {fabric} from 'fabric'

var LabeledRect = fabric.util.createClass(fabric.Rect, {
    type: 'labeledRect',

    initialize: function(options) {
        options || (options = { });
        this.callSuper('initialize', options);
        this.set('label', options.label || '');
    },

    toObject: function() {
        return fabric.util.object.extend(this.callSuper('toObject'), {
        label: this.get('label')
        });
    },

    _render: function(ctx) {
        this.callSuper('_render', ctx);
        ctx.font = '10px Helvetica';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(this.label, -this.width/2, -this.height/2 + 8);
    }
});


const LABELS = [
  {value: 'volvo', color: 'red'},
  {value: 'saab', color: 'green'},
  {value: 'opel', color: 'blue'},
  {value: 'audi', color: 'orange'}
]

const COLORS = {
    'volvo':'red',
    'saab':'green',
    'opel':'blue',
    'audi':'orange'
}

var SHAPE1 = {
    coords: {
        bl: {x: 145, y: 149},
        br: {x: 269, y: 149},
        tl: {x: 145, y: 46.99},
        tr: {x: 269, y: 46.99}
    },
    id: "s93pmd89nl",
    label: "volvo"
}

var SHAPE2 = {
    coords: {
        bl: {x: 361, y: 353},
        br: {x: 603, y: 353},
        tl: {x: 361, y: 255},
        tr: {x: 603, y: 255}
    },
    id: "asddddsss",
    label: "opel"
}

const DATA = {
    imgUrl: "http://www.nature.org/cs/groups/webcontent/@photopublic/documents/media/bluebird-640x400-1.jpg",
    imgHeight: 400,
    imgWidth: 640,
    shapes: [
        SHAPE1, 
        SHAPE2
    ]
}

var canvas;
var rect, isDown, origX, origY;
var isDrawing = true;


export default {
  name: 'editor',
  components: { fabric },
  
  data () {
    return {
      msg: 'Welcome to My7 Vue.js App',
      imgData: DATA,
      selectedLabel: LABELS[0].value,
      labels: LABELS,
      colors: COLORS
    }
  },

  mounted: function() {
    console.log(DATA);
    canvas = new fabric.Canvas('c');
    this.setupCanvas(canvas);
  },

  created: function () {
    console.log("VUE created!");
  },

  methods: {

    setupCanvas: function(canvas) {
      canvas.selection = false;    
      canvas.setDimensions({
          height: this.imgData.imgHeight,
          width: this.imgData.imgWidth
      });
      canvas.setBackgroundImage(this.imgData.imgUrl, 
          canvas.renderAll.bind(canvas));
      this.loadBBs(canvas, this.imgData.shapes);

      let self = this;
      canvas.on('mouse:down', function(o) {
        if (!isDrawing) {
          return;
        }
        isDown = true;
        var pointer = canvas.getPointer(o.e);
        origX = pointer.x;
        origY = pointer.y;
        var pointer = canvas.getPointer(o.e);
        rect = new LabeledRect({
          left: origX,
          top: origY,
          originX: 'left',
          originY: 'top',
          width: pointer.x - origX,
          height: pointer.y - origY,
          angle: 0,
          fill: self.getColor(),
          transparentCorners: false,
          selectable: false,
          label: self.getCurLabel(),
          id: self.getRandId(),
          opacity: 0.5
        });
        canvas.add(rect);
      });
    
      canvas.on('mouse:move', function(o) {
        if (!isDrawing) {
          return;
        }
      
        if (!isDown) return;
        var pointer = canvas.getPointer(o.e);
      
        if (origX > pointer.x) {
          rect.set({
            left: Math.abs(pointer.x)
          });
        }
        if (origY > pointer.y) {
          rect.set({
            top: Math.abs(pointer.y)
          });
        }
      
        rect.set({
          width: Math.abs(origX - pointer.x)
        });
        rect.set({
          height: Math.abs(origY - pointer.y)
        });
      
        canvas.renderAll();
        });
        
        canvas.on('mouse:up', function(o) {
          if (!isDrawing) {
            return;
          }
          rect.setCoords();
          isDown = false;
      });
    },

    loadBBs: function(canvas, shapes) {
      let top, left, bottom, right, width, height, bb;
      let self = this;
      for (let shape of shapes) {
          top = shape.coords.tl.y;
          left = shape.coords.tl.x;
          bottom = shape.coords.br.y;
          right = shape.coords.br.x;
          rect = new LabeledRect({
              left: left,
              top: top,            
              originX: 'left',
              originY: 'top',
              width: right - left,
              height: top - bottom,
              angle: 0,
              fill: self.colors[shape.label],
              transparentCorners: false,
              selectable: false,
              label: shape.label,
              id: shape.id,
              opacity: 0.5
          });
          canvas.add(rect);
      }
    },

    getColor: function () {
      let label = this.getCurLabel();
      return this.colors[label];
    },

    getCurLabel: function () {
        let select = document.getElementById("select-label");
        let value = select.options[select.selectedIndex].value;
        return value;
    },

    getRandId: function () {
        return Math.random().toString(36).substr(2, 10);
    },

    deleteObject: function () {
        let obj = canvas.getActiveObject();
        canvas.remove(obj);
    },

    extractCoords: function (rect) {
        let coords = {}
        let coordObj = rect.get('aCoords');
        for (let key of Object.keys(coordObj)) {
            coords[key] = {
                'x':coordObj[key]['x'],
                'y':coordObj[key]['y']
            }
        }
        return coords;
    },

    extractBBs: function () {
      console.log("extracting BBs");
        let bbs = [];
        let self = this;
        let bb;
        canvas.getObjects().map(function(o) {
            console.log(o);
            bb = {}
            bb.id = o.get('id');
            bb.label = o.get('label');
            bb.coords = self.extractCoords(o);
            let h = o.get('height');
            let w = o.get('width');
            if (h !== 0 && w !== 0) {
                bbs.push(bb);
            }
        });
        return bbs;    
    },

    save: function () {
      console.log("saving!");
        let bbs = this.extractBBs();
        console.log(bbs);
    },

    drawMode: function () {
        isDrawing = true;
        canvas.forEachObject(function(o) {
            o.selectable = false;
        }).selection = false;
    },

    selectMode: function() {
        isDrawing = false;
        canvas.forEachObject(function(o) {
        o.set({selectable: true}).setCoords();
        }).selection = true;  
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
