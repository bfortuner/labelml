<template>
  <div class="editor">
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
import { OBJ_DETECT_IMG_QUERY } from '../constants/graphql'
import { OBJ_DETECT_LABEL_OPT_QUERY } from '../constants/graphql'
import { SAVE_OBJ_DETECT_IMAGE } from '../constants/graphql'
import { NEXT_OBJ_DETECT_IMG_QUERY } from '../constants/graphql'



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


var canvas;
var rect, isDown, origX, origY;
var isDrawing = true;

export default {
  name: 'editor',
  components: { fabric },
  props: ['project'],
  data () {
    return {
      id: '',
      image: {},
      objDetectLabelOpts: [],
      selectedLabel: ''
    }
  },

  apollo: {
    // image: {
    //   query: OBJ_DETECT_IMG_QUERY,
    //   variables () {
    //     return {
    //       id: this.id,
    //       project: this.project 
    //     }
    //   },
    //   result({ data, loader, networkStatus }) {
    //     this.initializeCanvas();
    //   },
    // },
    nextObjDetectImage: {
      query: NEXT_OBJ_DETECT_IMG_QUERY,
      variables () {
        return {
          project: this.project 
        }
      },
      result({ data, loader, networkStatus }) {
        this.image = data.nextObjDetectImage;
        this.initializeCanvas();
        this.loadBBs();
      },
    },
    objDetectLabelOpts: {
      query: OBJ_DETECT_LABEL_OPT_QUERY,
      variables () {
        return {
          project: this.project 
        }
      },
      result({ data, loader, networkStatus }) {
        this.selectedLabel = data.objDetectLabelOpts.labels[0].value;
        this.loadBBs();
      },
    }   
  },

  computed: {
    labels: function() {
      return this.objDetectLabelOpts.labels;
    },
    colors: function () {
      let colorMap = {}
      for (let opt of this.objDetectLabelOpts.labels) {
        colorMap[opt.value] = opt.color;
      }
      return colorMap;
    }
  },

  mounted: function() {
    return
  },

  created: function () {
    return
  },

  methods: {

    initializeCanvas: function () {
      if (canvas == null) { 
        canvas = new fabric.Canvas('c');
      } else {
        canvas.dispose();
        canvas = new fabric.Canvas('c');
      }
      var img = new Image();
      var self = this;
      img.onload = function() {
        self.configureCanvas(this.width, this.height);
      }
      img.src = this.image.src;
    },

    configureCanvas: function(width, height) {
      canvas.selection = false;
      canvas.setDimensions({
          height: height,
          width: width
      });
      canvas.setBackgroundImage(
        this.image.src, 
          canvas.renderAll.bind(canvas));

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

    loadBBs: function() {
      let shapes = this.image.boundingBoxes;
      let self = this;
      for (let shape of shapes) {
        rect = new LabeledRect({
          left: shape.coords.x,
          top: shape.coords.y,            
          originX: 'left',
          originY: 'top',
          width: shape.coords.width,
          height: shape.coords.height,
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
    
    extractCoords: function (rect) {
      let coords = rect.get('aCoords');
      return {
        'x': coords['tl']['x'],
        'y': coords['tl']['y'],
        'width': coords['tr']['x'] - coords['tl']['x'],
        'height': coords['br']['y'] - coords['tr']['y'],
      }
    },

    extractBBs: function () {
      let bbs = [];
      let self = this;
      let bb;
      canvas.getObjects().map(function(o) {
        bb = {}
        bb.id = o.get('id');
        bb.label = o.get('label');
        bb.coords = self.extractCoords(o);
        if (bb.coords.height !== 0 && bb.coords.width !== 0) {
            bbs.push(bb);
        }
      });
      return bbs;    
    },

    getNextImg: function () {
      this.$apollo.queries.nextObjDetectImage.refetch();
    },

    save: function () {
      let bbs = this.extractBBs();
      console.log(bbs);
      this.$apollo.mutate({
        mutation: SAVE_OBJ_DETECT_IMAGE,
        variables: {
          id: this.image.id,
          project: this.project,
          boundingBoxes: bbs
        }
      }).then((data) => {
        this.$apollo.queries.nextObjDetectImage.refetch();
      })
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
