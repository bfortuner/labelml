<template>
  <div class="editor">
    <button @click="getNextImg()">Next</button>
    <button @click="save()">Save</button>
    <button @click="deleteObject()">Delete</button>
    <button @click="setDrawMode()">Draw box</button>
    <button @click="setExtremeClickMode()">Click-to-box</button>
    <button @click="setSelectMode()">Select</button>
    <select id='select-label' v-model="selectedLabel">
      <option v-for="label in labels"
            v-bind:value="label.value" :key="label.value">
        {{ label.value }}
      </option>
    </select>
    <range-slider
      class="slider"
      min="0"
      max="1"
      step=".05"
      v-model="sliderValue"
      v-on="adjustThreshold()">
    </range-slider>
    <canvas id="c"></canvas>
  </div>
</template>

<script>
import {fabric} from 'fabric'
import RangeSlider from 'vue-range-slider'
import 'vue-range-slider/dist/vue-range-slider.css'
import { OBJ_DETECT_IMG_QUERY } from '../constants/graphql'
import { OBJ_DETECT_LABEL_OPT_QUERY } from '../constants/graphql'
import { SAVE_OBJ_DETECT_IMAGE } from '../constants/graphql'
import { NEXT_OBJ_DETECT_IMG_QUERY } from '../constants/graphql'


window.onkeydown = onKeyDownHandler;

function onKeyDownHandler(e) {
  print(e);
  let obj = canvas.getActiveObject();

  // Shrink box
  if (e.keyCode === 37 && e.shiftKey && e.altKey) {
    print("shrink left");
    e.preventDefault();
    e.stopImmediatePropagation()
    obj.set({width: obj.width -= 5});
  } else if (e.keyCode === 39 && e.shiftKey && e.altKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("shrink right");
    obj.set({width: obj.width -= 5})//.setCoords();
    obj.set({left: obj.left += 5});
  } else if (e.keyCode === 38 && e.shiftKey && e.altKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("shrink top");
    obj.set({height: obj.height -= 5});
  } else if (e.keyCode === 40 && e.shiftKey && e.altKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("shrink bottom");
    obj.set({height: obj.height -= 5})
    obj.set({top: obj.top += 5});

  // Stretch box
  } else if (e.keyCode === 37 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("stretch left");
    obj.set({width: obj.width += 5})//.setCoords();
    obj.set({left: obj.left -= 5});
  } else if (e.keyCode === 39 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("stretch right");
    obj.set({width: obj.width += 5});
  } else if (e.keyCode === 38 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("stretch top");
    obj.set({height: obj.height += 5})
    obj.set({top: obj.top -= 5});
  } else if (e.keyCode === 40 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("stretch bottom");
    obj.set({height: obj.height += 5});

  // Move box
  } else if (e.keyCode === 37) {
    e.preventDefault();
    e.stopImmediatePropagation();
    print("move LEFT");
    obj.set({left: obj.left -= 5});
  } else if (e.keyCode === 39) {
    print("move RIGHT");
    e.preventDefault();
    e.stopImmediatePropagation();
    obj.set({left: obj.left += 5});
  } else if (e.keyCode === 38) {
    print("move UP");
    e.preventDefault();
    e.stopImmediatePropagation();
    obj.set({top: obj.top -= 5});
  } else if (e.keyCode === 40) {
    print("move DOWN");
    e.preventDefault();
    e.stopImmediatePropagation();
    obj.set({top: obj.top += 5});
  }
  canvas.renderAll();
  return;
};

var print = function(text) {
  console.log(text);
}

var LabeledRect = fabric.util.createClass(fabric.Rect, {
    type: 'labeledRect',

    initialize: function(options) {
        options || (options = { });
        this.callSuper('initialize', options);
        this.set('label', options.label || '');
        this.set('score', options.score || 1.0);
    },

    toObject: function() {
        return fabric.util.object.extend(
          this.callSuper('toObject'), {
            label: this.get('label'),
            score: this.get('score')
        });
    },

    _render: function(ctx) {
        this.callSuper('_render', ctx);
        let score = Math.round(this.score * 100) / 100;
        let text = this.label + " (" + score + ")";
        ctx.font = '10px Helvetica';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(text, -this.width/2, -this.height/2 + 8);
    }
});


var canvas;
var rect, isDown, origX, origY;
var isDrawing = true;

export default {
  name: 'editor',
  components: { 
    fabric,
    RangeSlider
  },
  props: ['project'],
  
  data () {
    return {
      id: '',
      image: {},
      objDetectLabelOpts: [],
      selectedLabel: '',
      sliderValue: 1.0,
      clickRadius: 3,
      hideUnselected: false,
      selectMode: true,
      drawMode: false,
      extremeClickMode: false,
      extremeClicks: []
    }
  },
  
  apollo: {
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
    let self = this;
    window.addEventListener('keyup', function(e) {
      if (e.keyCode == 83 && e.ctrlKey) { // ctrl + s
        self.save();
      } else if (e.keyCode == 67) { // c
        self.setExtremeClickMode();
      } else if (e.keyCode == 78) { // n
        self.getNextImg();
      } else if (e.keyCode == 83) { // s
        self.setSelectMode();
      } else if (e.keyCode == 68) { // d
        e.preventDefault();
        e.stopImmediatePropagation();
        self.setDrawMode();
      } else if (e.keyCode == 72) { // h
        e.preventDefault();
        e.stopImmediatePropagation();
        self.toggleUnselectedVisibility(true);
        print('pressing h');
      // Shift 9 but giving bugs
      } else if (e.keyCode == 9 && e.shiftKey) { // tab
        e.preventDefault();
        e.stopImmediatePropagation();
        self.navigateNextBox('left');
      } else if (e.keyCode == 9) { // tab
        e.preventDefault();
        e.stopImmediatePropagation();
        self.navigateNextBox('right');
      } else if (e.keyCode == 65 && e.ctrlKey) { // a
        e.preventDefault();
        e.stopImmediatePropagation();
        self.navigateNextBox('left');
      } else if (e.keyCode == 69 && e.ctrlKey) { // e
        e.preventDefault();
        e.stopImmediatePropagation();
        self.navigateNextBox('right');
      } else if (e.keyCode === 27) { // ESC
        e.preventDefault();
        e.stopImmediatePropagation();
        self.deselectObject();
      } else if (e.keyCode === 46 || e.keyCode === 8) {
        self.deleteObject();
      }
    });
  },

  methods: {
    initializeCanvas: function () {
      let self = this;
      if (canvas == null) { 
        canvas = new fabric.Canvas('c');
      } else {
        canvas.dispose();
        canvas = new fabric.Canvas('c');
      }
      var img = new Image();
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

      //https://github.com/kangax/fabric.js/wiki/Working-with-events
      canvas.on({
        'mouse:down': this.mouseDownHandler,
        'mouse:up': this.mouseUpHandler,
        'mouse:move': this.mouseMoveHandler
      });
      this.setSelectMode();
      canvas.renderAll();
    },

    mouseDownHandler: function(o) {
      console.log("Mouse down");
      isDown = true;
      if (this.extremeClickMode) {
        this.initExtremeClick(o);
      } else if (isDrawing) {
        this.initRectangle(o);
      } else {
        return;
      }
    },

    initRectangle: function(o) {
      console.log('handling draw');
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
        fill: this.getColor(),
        transparentCorners: false,
        selectable: true,
        label: this.getCurLabel(),
        id: this.getRandId(),
        opacity: 0.3,
        visible: true
      });
      canvas.add(rect);  
    },

    initExtremeClick: function(o) {
      console.log('init extreme click');
    },

    saveRectangle: function(o) {
      console.log('saving rectangle');
      rect.set({
        score: 1.0
      });
      rect.setCoords();
      canvas.setActiveObject(rect);
      this.setSelectMode();
    },

    saveExtremeClick: function(o) {
      console.log('saving extreme click');
      let pointer = canvas.getPointer(o.e);
      let circle = new fabric.Circle({
        radius: this.clickRadius, 
        fill: 'blue', 
        left: this.getXCoordFromClick(pointer),
        top: this.getYCoordFromClick(pointer)
      });
      console.log(pointer.x, pointer.y, circle.left, circle.top);
      canvas.add(circle);
      this.extremeClicks.push(circle);
      if (this.extremeClicks.length === 4) {
        this.createBoxFromExtremeClicks();
      }
      console.log("current clicks", this.extremeClicks.length);
    },

    getXCoordFromClick: function(pointer) {
      console.log(pointer);
      return pointer.x - this.clickRadius;
    },

    getYCoordFromClick: function(pointer) {
      return pointer.y - this.clickRadius;
    },

    createBoxFromExtremeClicks: function() {
      console.log('creating box from extreme clicks');
      let r, click, xmin, ymin, xmax, ymax;
      for (let i in this.extremeClicks) {
        click = this.extremeClicks[i];
        if (xmin === undefined || click.left < xmin) {
          xmin = click.left;
        }
        if (ymin === undefined || click.top < ymin) {
          ymin = click.top;
        }
        if (xmax === undefined || click.left > xmax) {
          xmax = click.left;
        }
        if (ymax === undefined || click.top > ymax) {
          ymax = click.top;
        }
        console.log(this.extremeClicks[i]);
      }
      xmin += this.clickRadius;
      ymin += this.clickRadius;
      xmax += this.clickRadius;
      ymax += this.clickRadius;
      r = this.createRectFromCoords(xmin, ymin, xmax, ymax);
      canvas.setActiveObject(r);
      this.resetExtremeClicks();
      canvas.renderAll();
      this.setSelectMode();
    },

    resetExtremeClicks: function() {
      for (let i in this.extremeClicks) {
        canvas.remove(this.extremeClicks[i]);  
      }
      this.extremeClicks = [];
      this.extremeClickMode = false;
    },

    createRectFromCoords: function(xmin, ymin, xmax, ymax) {
      rect = new LabeledRect({
        left: xmin,
        top: ymin,
        originX: 'left',
        originY: 'top',
        width: xmax - xmin,
        height: ymax - ymin,
        angle: 0,
        fill: this.getColor(),
        transparentCorners: false,
        selectable: true,
        label: this.getCurLabel(),
        id: this.getRandId(),
        opacity: 0.3,
        visible: true
      });
      canvas.add(rect);
      return rect;
    },

    mouseUpHandler: function(o) {
      console.log("Mouse up");
      isDown = false;
      if (this.extremeClickMode) {
        this.saveExtremeClick(o);
      } else if (isDrawing) {
        this.saveRectangle(o);
      } else {
        return;
      }
      canvas.renderAll();
    },

    mouseMoveHandler: function(o) {
      if (!isDrawing || !isDown) {
        return;
      }
      if (this.extremeClickMode) {
        this.handleExtremeClickMove(o);
      } else if (this.drawMode || isDrawing) {
        this.handleDrawMove(o);
      } else {
        return;
      }
      canvas.renderAll();
    },

    handleDrawMove: function(o) {
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
    },

    loadBBs: function() {
      let shapes = this.image.bboxes;
      let self = this;
      for (let shape of shapes) {
        rect = new LabeledRect({
          left: shape.xmin,
          top: shape.ymin,            
          originX: 'left',
          originY: 'top',
          width: shape.xmax - shape.xmin,
          height: shape.ymax - shape.ymin,
          angle: 0,
          fill: self.colors[shape.label],
          transparentCorners: false,
          selectable: false,
          label: shape.label,
          id: shape.id,
          opacity: 0.3,
          visible: shape.score >= this.sliderValue,
          score: shape.score
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

    deselectObject: function () {
      canvas.discardActiveObject();
      canvas.renderAll();
    },
    
    extractBB: function (rect) {
      let bb = {}
      let coords = rect.get('aCoords');
      bb.id = rect.get('id');
      bb.label = rect.get('label');
      bb.score = rect.get('score');
      bb.xmin = coords['tl']['x'],
      bb.ymin = coords['tl']['y'],
      bb.xmax = coords['tr']['x'],
      bb.ymax = coords['br']['y']
      return bb
    },

    extractBBs: function () {
      let bbs = [];
      let self = this;
      let bb, width, height;
      canvas.getObjects().map(function(o) {
        bb = self.extractBB(o);
        width = bb.xmax - bb.xmin;
        height = bb.ymax - bb.ymin;
        if (width !== 0 && height !== 0 && bb.score >= self.sliderValue) {
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
      console.log("Saving bbs", bbs);
      this.$apollo.mutate({
        mutation: SAVE_OBJ_DETECT_IMAGE,
        variables: {
          id: this.image.id,
          project: this.project,
          bboxes: bbs
        }
      }).then((data) => {
        this.$apollo.queries.nextObjDetectImage.refetch();
      })
    },

    setDrawMode: function () {
      this.deselectObject();
      this.resetExtremeClicks();
      isDrawing = true;
      this.drawMode = true;
      canvas.forEachObject(function(o) {
        o.selectable = false;
      }).selection = false;
      
    },

    setSelectMode: function() {
      isDrawing = false;
      this.drawMode = false;
      this.resetExtremeClicks();
      canvas.forEachObject(function(o) {
        o.set({selectable: true}).setCoords();
      }).selection = true;
      let obj = canvas.getActiveObject();
      if (obj === undefined) {
        this.setDefaultObject();
      }
    },

    getBoxScore: function(id) {
      let box = null;
    },

    adjustThreshold: function() {
      let self = this;
      if (canvas !== undefined) {
        canvas.forEachObject(function(o) {
          o.visible = o.score >= self.sliderValue;
        })
        canvas.renderAll();
      }
    },

    navigateNextBox: function(direction) {
      print("Navigating " + direction);
      let self = this;
      let curBox = canvas.getActiveObject();
      canvas.discardActiveObject();
      let boxes = [];
      canvas.forEachObject(function(o) {
        if (o.score >= self.sliderValue) {
          boxes.push(o);
        }
      })
      console.log("curBox", curBox['left'], curBox['id'])
      console.log("unsorted", boxes)
      console.log("firstbox", boxes[0]['left'])
      this.sortBoxesByProp(boxes, 'left');
      console.log("sorted", boxes);
      console.log("sortedfirstbox", boxes[0]['left'])
      let box;
      for (let i=0; i<boxes.length; i++) {
        print(direction);
        print(direction === "left");
        box = boxes[i];
        if (box.id === curBox.id) {
          print("Found box");
          if (direction === 'right') {
            print("DIRECTION is right")
            if (i+1 < boxes.length) {
              console.log("Rightnext", boxes[i+1].id, boxes[i+1].left);
              self.setCurrentObject(boxes[i+1]);
            } else {
              console.log("Rightfirst", boxes[0].id, boxes[0].left);
              self.setCurrentObject(boxes[0]);
            }
          } else {
            print("DIRECTION is left")
            if (i === 0) {
              self.setCurrentObject(boxes[boxes.length-1]);
            } else {
              self.setCurrentObject(boxes[i-1]);
            }
          }
        } else {
          print("Not box " + i);
        }
      }
      self.toggleUnselectedVisibility(false);
      canvas.renderAll();
    },

    setCurrentObject: function(box) {
      box.visible = true;
      box.selectable = true;
      canvas.setActiveObject(box);
      canvas.renderAll();
    },

    deleteObject: function() {
      let objs = canvas.getActiveObject();
      if (objs !== undefined && objs !== null) {
        if (objs._objects instanceof Array) {
          for (let i in objs._objects) {
            canvas.remove(objs._objects[i]);
          }
        } else {
          canvas.remove(objs);
        }
        canvas.renderAll();
        this.setDefaultObject();
      }
    },

    setDefaultObject: function() {
      if (canvas !== undefined) {
        let boxes = canvas.getObjects();
        console.log("LEN", boxes.length);
        this.sortBoxesByProp(boxes, 'left');
        for (let i in boxes) {
          console.log("box", boxes[i].score, this.sliderValue);
          if (boxes[i].score >= this.sliderValue) {
            print("FOUND BOX")
            canvas.setActiveObject(boxes[i]);
            break;
          }
        }
        canvas.renderAll();
      }
    },

    sortBoxesByProp: function(boxes, prop) {
      boxes.sort(function(a, b) { 
        return a[prop] - b[prop];
      })
    },

    getBoxById: function(boxes, id) {
      for (let box of boxes) {
        console.log(box.id, box.score, box.xmin);
        if (box.id === id) {
          return box;
        }
      }
    },
    
    setExtremeClickMode: function() {
      this.deselectObject();
      this.extremeClickMode = true;
      this.extremeClicks = [];
      console.log("Entering extreme click mode");
    },

    toggleUnselectedVisibility: function(updateToggle) {
      print('toggling visibility', updateToggle);
      if (updateToggle) {
        console.log("Updating toggle", this.hideUnselected, !this.hideUnselected);
        this.hideUnselected = !this.hideUnselected;
      } 
      let curBox = canvas.getActiveObject();
      let allBoxes = canvas.getObjects();
      for (let box of allBoxes) {
        if (box.id !== curBox.id) {
          console.log("SCORE", box.score);
          if (box.score < this.sliderValue) {
            box.visible = false;
          } else {
            console.log("Making visible", !this.hideUnselected);
            box.visible = !this.hideUnselected;
          }
        }
      }
      canvas.renderAll();
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


.slider {
  /* overwrite slider styles */
  width: 200px;
}
</style>
