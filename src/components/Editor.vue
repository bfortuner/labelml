<template>
  <div class="editor">
    <button @click="getNextImg()">Next</button>
    <button @click="save()">Save</button>
    <button @click="deleteObject()">Delete</button>
    <button @click="setDrawMode()">Box</button>
    <button @click="setExtremeClickMode()">Click-to-box</button>
    <button @click="setPolygonMode()">Polygon</button>
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
    <!-- <vue-slider
      class="slider"
      min=0
      max=1
      interval=.05
      v-model="sliderValue"
      v-on="adjustThreshold()">
    </vue-slider> -->
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

const BOX_LABEL = 'box';
const EC_LABEL = 'extremeClick';
const POLY_CLICK_LABEL = 'polygonClick';
const POLYGON_LABEL = 'polygon';
const POLY_LINE_LABEL = 'polygonLine';
const LABEL_TYPES = [
  BOX_LABEL,
  EC_LABEL,
  POLYGON_LABEL,
  POLY_CLICK_LABEL,
  POLY_LINE_LABEL,
]

window.onkeydown = onKeyDownHandler;

function onKeyDownHandler(e) {
  // print(e);
  let obj = canvas.getActiveObject();

  // Shrink box
  if (e.keyCode === 37 && e.shiftKey && e.altKey) {
    // print("shrink left");
    e.preventDefault();
    e.stopImmediatePropagation()
    obj.set({width: obj.width -= 5});
  } else if (e.keyCode === 39 && e.shiftKey && e.altKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("shrink right");
    obj.set({width: obj.width -= 5})//.setCoords();
    obj.set({left: obj.left += 5});
  } else if (e.keyCode === 38 && e.shiftKey && e.altKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("shrink top");
    obj.set({height: obj.height -= 5});
  } else if (e.keyCode === 40 && e.shiftKey && e.altKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("shrink bottom");
    obj.set({height: obj.height -= 5})
    obj.set({top: obj.top += 5});

  // Stretch box
  } else if (e.keyCode === 37 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("stretch left");
    obj.set({width: obj.width += 5})//.setCoords();
    obj.set({left: obj.left -= 5});
  } else if (e.keyCode === 39 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("stretch right");
    obj.set({width: obj.width += 5});
  } else if (e.keyCode === 38 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("stretch top");
    obj.set({height: obj.height += 5})
    obj.set({top: obj.top -= 5});
  } else if (e.keyCode === 40 && e.shiftKey) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("stretch bottom");
    obj.set({height: obj.height += 5});

  // Move box
  } else if (e.keyCode === 37) {
    e.preventDefault();
    e.stopImmediatePropagation();
    // print("move LEFT");
    obj.set({left: obj.left -= 5});
  } else if (e.keyCode === 39) {
    // print("move RIGHT");
    e.preventDefault();
    e.stopImmediatePropagation();
    obj.set({left: obj.left += 5});
  } else if (e.keyCode === 38) {
    // print("move UP");
    e.preventDefault();
    e.stopImmediatePropagation();
    obj.set({top: obj.top -= 5});
  } else if (e.keyCode === 40) {
    // print("move DOWN");
    e.preventDefault();
    e.stopImmediatePropagation();
    obj.set({top: obj.top += 5});
  } else if (e.keyCode == 9) { // tab
      e.preventDefault();
      e.stopImmediatePropagation();
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
  
  data() {
    return {
      id: '',
      image: {},
      selectedLabel: '',
      sliderValue: 1.0,
      clickRadius: 3.5,
      hideUnselected: false,
      selectMode: true,
      drawMode: false,
      extremeClickMode: false,
      extremeClicks: [],
      polygonMode: false,
      polygonX: [],
      polygonY: [],
      cornerSize: 8,
      extremeClickRadius: 4,
      polyClickRadius: 3,
      polygonClicks: [],
      labels: [],
      colors: {},
      rects: []
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
        this.labels = data.nextObjDetectImage.labels;
        this.colors = this.makeColors(this.labels);
        this.selectedLabel = this.labels[0].value;
        this.initializeCanvas();
        this.loadAnnotations();
      },
    },
  },
  
  computed: {

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
      } else if (e.keyCode == 80) { // p <<<
        self.setPolygonMode();
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
    makeColors: function (labels) {
      let colorMap = {}
      for (let opt of labels) {
        colorMap[opt.value] = opt.color;
      }
      return colorMap;
    },

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
      
      this.setCornerSize(this.cornerSize);
      //https://github.com/kangax/fabric.js/wiki/Working-with-events
      canvas.on({
        'mouse:down': this.mouseDownHandler,
        'mouse:up': this.mouseUpHandler,
        'mouse:move': this.mouseMoveHandler,
        'object:moving': this.objectMovingHandler,
        'mouse:over': this.mouseOverHandler,
        'mouse:out': this.mouseOutHandler,
      });
      this.setSelectMode();
      canvas.renderAll();
    },

    objectMovingHandler: function(e) {
      if (this.extremeClickMode) {
        return;
      } else if (this.polygonMode) {
        this.adjustPolygonClick(e);
      } else if (isDrawing) {
        this.initRectangle(e);
      } else {
        return;
      }
    },

    mouseOverHandler: function(e) {
      //console.log("object over");
      if (this.extremeClickMode) {
        return;
      } else if (this.polygonMode) {
        this.handlePolygonMouseOver(e);
      } else if (this.drawMode) {
        return;
      } else {
        return;
      }
    },

    mouseOutHandler: function(e) {
      //console.log("object over");
      if (this.extremeClickMode) {
        return;
      } else if (this.polygonMode) {
        this.handlePolygonMouseOut(e);
      } else if (this.drawMode) {
        return;
      } else {
        return;
      }
    },

    mouseDownHandler: function(e) {
      //console.log("Mouse down", e.e.target);
      isDown = true;
      if (this.extremeClickMode) {
        this.initExtremeClick(e);
      } else if (this.polygonMode) {
        this.initPolygon(e);
      } else if (isDrawing) {
        this.initRectangle(e);
      } else {
        return;
      }
    },

    initRectangle: function(e) {
      //console.log('handling draw');
      var pointer = canvas.getPointer(e.e);
      origX = pointer.x;
      origY = pointer.y;
      var pointer = canvas.getPointer(e.e);
      rect = new LabeledRect({
        id: this.getRandId(),
        annoId: this.getRandId(),
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
        opacity: 0.3,
        visible: true,
        transparentCorners: true,
        cornerSize: this.cornerSize,
        labelType: BOX_LABEL,
        points: []
      });
      canvas.add(rect);  
    },

    getObjectById: function(id) {
      let objs = canvas.getObjects();
      for (let i=0; i<objs.length; i++) {
        console.log(objs[i]);
        if (objs[i] !== undefined && objs[i] !== null && objs[i].id === id) {
          return objs[i];
        }
      }
    },

    removeObjectById: function(id) {
      canvas.forEachObject(function(o) {
        if (o !== undefined && o !== null && o.id === id) {
          canvas.remove(o);
          canvas.renderAll();
          return;
        }
      });
    },

    initExtremeClick: function(e) {
      //console.log('init extreme click');
    },

    initPolygon: function(e) {
      console.log('init polygon click', canvas.getActiveObject());
      
    },

    saveRectangle: function(e) {
      //console.log('saving rectangle');
      rect.set({
        score: 1.0
      });
      rect.setCoords();
      canvas.setActiveObject(rect);
      this.setSelectMode();
    },

    saveExtremeClick: function(e) {
      let pointer = canvas.getPointer(e.e);
      let circle = new fabric.Circle({
        id: this.getRandId(),
        radius: this.extremeClickRadius, 
        fill: 'blue', 
        left: this.getXCoordFromClick(pointer, this.extremeClickRadius),
        top: this.getYCoordFromClick(pointer, this.extremeClickRadius),
        visible: true,
        score: 1.0,
        labelType: EC_LABEL,
      });
      canvas.add(circle);
      this.extremeClicks.push(circle.id);
      canvas.renderAll();
      if (this.extremeClicks.length === 4) {
        this.createBoxFromExtremeClicks();
      }
    },

    savePolygonClick: function(e) {
      console.log('saving polygon click');
      let pointer = canvas.getPointer(e.e);
      let circle = new fabric.Circle({
          id: this.getRandId(),
          strokeWidth: 1,
          radius: this.polyClickRadius,
          fill: '#fff',
          stroke: '#666',
          opacity: 0.8,
          left: this.getXCoordFromClick(pointer, this.polyClickRadius),
          top: this.getYCoordFromClick(pointer, this.polyClickRadius),
          hasControls: false,
          hasBorders: true,
          selectable: true,
          borderColor: 'white',
          padding: 3,
          labelType: POLY_CLICK_LABEL,
          hoverCursor: 'pointer'
        });

      if (this.polygonClicks.length === 0) {
        // circle.selectable = true;
        circle.lineIn = null;
        circle.set({
          radius: circle.radius*1.5,
          left: this.getXCoordFromClick(pointer, circle.radius*1.5),
          top: this.getYCoordFromClick(pointer, circle.radius*1.5),
          fill: 'blue',
        })
        canvas.add(circle);
        this.polygonClicks.push(circle.id);
      } else {
        let startCircle = this.getObjectById(
          this.polygonClicks[this.polygonClicks.length-1]);
        let line = this.makePolygonLine(startCircle, circle);
        circle.lineIn = line;
        startCircle.lineOut = line;
        canvas.add(line);
        canvas.add(circle);
        this.polygonClicks.push(circle.id);
      }
      canvas.setActiveObject(circle);
      canvas.bringToFront(circle);
      canvas.renderAll();
    },

    makePointsFromCoords: function(coords) {
      let self = this;
      coords.map(function(o) {
        o.id = self.getRandId();
      });
      return coords;
    },

    makePolygon: function() {
      console.log("Saving active polygon");
      let coords = [];
      let click, x, y;
      for (let id of this.polygonClicks) {
        click = this.getObjectById(id);
        coords.push({
          'x': click.left + click.radius,
          'y': click.top + click.radius
        })
      }
      console.log(coords);
      let polygon = new fabric.Polygon(coords, {
        id: this.getRandId(),
        annoId: this.getRandId(),
        label: this.getCurLabel(),
        fill: this.getColor(),
        selectable: false,
        objectCaching: false,
        opacity: 0.3,
        hasControls: false,
        hasBorders: true,
        borderColor: 'white',
        cornerStyle: 'circle',
        cornerColor: 'white',
        cornerSize: 3,
        labelType: POLYGON_LABEL,
        score: 1.0,
        points: this.makePointsFromCoords(coords),
      });
      return polygon;
    },

    savePolygon: function() {
      let polygon = this.makePolygon();
      canvas.add(polygon);
      // Update labels.json
      this.resetPolygonMode();
      this.setSelectMode();
      canvas.setActiveObject(polygon);
    },

    adjustPolygonClick: function(e) {
      //console.log("adjusting polygon click");
      let activeObj = canvas.getActiveObject();
      let idx = this.polygonClicks.indexOf(activeObj.id);
      //console.log(activeObj.lineIn, activeObj.lineOut);
      if (activeObj.lineIn !== undefined && activeObj.lineIn !== null) {
        activeObj.lineIn.set({
           'x2': activeObj.left + activeObj.radius, 
           'y2': activeObj.top + activeObj.radius 
        });
      }
      if (activeObj.lineOut !== undefined && activeObj.lineOut !== null) {
        activeObj.lineOut.set({
           'x1': activeObj.left + activeObj.radius, 
           'y1': activeObj.top + activeObj.radius
        });
      }
      if (this.exists(this.polygon)) {
        console.log('polygon exists', this.polygon.points);
        this.polygon.points[idx] = {
          'x': activeObj.left + activeObj.radius, 
          'y': activeObj.top + activeObj.radius
        };
      }
      canvas.renderAll();
    },

    handlePolygonClick: function(e) {
      let activeObj = canvas.getActiveObject();
      if (this.exists(this.polygon)) {
        return;
      } else if (this.polygonClicks.length === 0) {
        this.savePolygonClick(e);
      } else if (activeObj === undefined || activeObj === null) {
        this.savePolygonClick(e);
      } else if (this.polygonClicks[0] === activeObj.id && !this.exists(this.polygon)) {
        this.savePolygon();
      } else if (this.polygonClicks.includes(activeObj.id)) {
        //console.log(activeObj.get('type'));
        //this.adjustPolygonClick(e);
      } else {
        //console.log("not recognize action");
        return;
      }
    },

    handlePolygonMouseOver: function(e) {
      console.log("poly point hover", e.target);
      let obj = e.target;
      if (obj !== undefined 
          && obj !== null
          && this.polygonClicks.length > 0
          && obj === this.polygonClicks[0]) {
        obj.set({
          stroke: 'green',
          fill: 'green',
        });
        canvas.renderAll();
      }
    },

    handlePolygonMouseOut: function(e) {
      console.log("poly point out", e.target);
      let obj = e.target;
      if (obj !== undefined 
          && obj !== null
          && this.polygonClicks.length > 0
          && obj === this.polygonClicks[0]) {
        obj.set({
          stroke: 'blue',
          fill: 'blue'
        });
        canvas.renderAll();
      }
    },

    makePolygonLine: function(startCircle, endCircle) {
      let coords = [
        startCircle.left + startCircle.radius, 
        startCircle.top + startCircle.radius, 
        endCircle.left + endCircle.radius, 
        endCircle.top + endCircle.radius
      ]
      //console.log("coords", coords);
      return new fabric.Line(coords, {
        id: this.getRandId(),
        fill: 'white',
        stroke: 'white',
        strokeWidth: 1,
        selectable: false,
        hasControls: false,
        labelType: POLY_LINE_LABEL,
        score: 1.0,
        //https://www.w3schools.com/cssref/playit.asp?filename=playcss_cursor&preval=context-menu
        hoverCursor: 'default',
      });
    },

    getXCoordFromClick: function(pointer, radius) {
      return pointer.x - radius;
    },

    getYCoordFromClick: function(pointer, radius) {
      return pointer.y - radius;
    },

    makePoint: function(click) {
      return {
        'id': click.id,
        'x': click.left += click.radius,
        'y': click.top += click.radius,
      }
    },

    createBoxFromExtremeClicks: function() {
      console.log('creating box from extreme clicks', this.extremeClicks);
      let r, click, xmin, ymin, xmax, ymax;
      let points = [];
      for (let i=0; i<this.extremeClicks.length; i++) {
        console.log("ID", this.extremeClicks[i]);
        click = this.getObjectById(this.extremeClicks[i]);
        points.push(this.makePoint(click));
        console.log(click);
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
      }
      xmin += this.clickRadius;
      ymin += this.clickRadius;
      xmax += this.clickRadius;
      ymax += this.clickRadius;
      r = this.createRectFromCoords(xmin, ymin, xmax, ymax);
      r.points = points;
      canvas.setActiveObject(r);
      this.resetExtremeClicks();
    },

    resetExtremeClicks: function() {
      while (this.extremeClicks.length > 0){
        this.removeObjectById(this.extremeClicks[0]);
        this.extremeClicks.splice(0, 1);
      }
      this.extremeClickMode = false;
    },

    exists: function(obj) {
      return obj !== undefined && obj !== null;  
    },

    deletePolygonClick: function(click) {
      let idx = this.polygonClicks.indexOf(click.id);
      console.log("IDX", idx, this.polygonClicks.length);
      if (idx === this.polygonClicks.length-1) {
        canvas.remove(click.lineIn);
      } else if (idx === 0 && this.exists(click.lineOut)) {
        canvas.remove(click.lineOut);
      } else if (this.exists(click.lineIn) && this.exists(click.lineOut)) {
        let priorClick = this.getObjectById(this.polygonClicks[idx-1]);
        let nextClick = this.getObjectById(this.polygonClicks[idx+1]);
        priorClick.lineOut.set({
           'x2': click.lineOut.x2,
           'y2': click.lineOut.y2
        });
        nextClick.set({
           'lineIn': priorClick.lineOut
        });
        canvas.remove(click.lineOut);
      } else {
        canvas.remove(click.lineIn);
        canvas.remove(click.lineOut);
      }
      canvas.remove(click);
      if (idx > 0) {
        print("SETTING active idx " + idx);
        let obj = this.getObjectById(this.polygonClicks[idx-1])
        console.log("O", obj, this.polygonClicks[idx-1]);
        canvas.setActiveObject(obj);
        canvas.renderAll();
      }
      this.polygonClicks.splice(idx, 1);
      console.log("PCS", this.polygonClicks);
      if (this.exists(this.polygon)) {
        console.log("polygon exists");
        canvas.remove(this.polygon);
        this.savePolygon();
      }
    },

    resetPolygonMode: function() {
      if (this.exists(this.polygon)) {
        //save to labels.json and reload static
        console.log('polygon exists');
      }
      while (this.polygonClicks.length > 0) {
        let idx = this.polygonClicks.length - 1;
        let click = this.getObjectById(this.polygonClicks[idx])
        this.deletePolygonClick(click);
      }
      this.polygonMode = false;
      this.polygon = null;
    },

    createRectFromCoords: function(xmin, ymin, xmax, ymax) {
      let rect = new LabeledRect({
        id: this.getRandId(),
        annoId: this.getRandId(),
        left: xmin,
        top: ymin,
        originX: 'left',
        originY: 'top',
        width: xmax - xmin,
        height: ymax - ymin,
        angle: 0,
        fill: this.getColor(),
        selectable: true,
        label: this.getCurLabel(),
        opacity: 0.3,
        visible: true,
        transparentCorners: true,
        cornerSize: this.cornerSize,
        score: 1.0,
        labelType: BOX_LABEL
      });
      canvas.add(rect);
      canvas.bringToFront(rect)
      canvas.renderAll();
      return rect;
    },

    mouseUpHandler: function(e) {
      console.log("Mouse up");
      isDown = false;
      if (this.extremeClickMode) {
        this.saveExtremeClick(e);
      } else if (this.polygonMode) {
        this.handlePolygonClick(e);        
      } else if (isDrawing) {
        this.saveRectangle(e);
      } else {
        return;
      }
      canvas.renderAll();
    },

    mouseMoveHandler: function(e) {
      if (!isDrawing || !isDown) {
        return;
      }
      if (this.extremeClickMode) {
        //this.handleExtremeClickMove(e);
      // } else if (this.polygonMode) {
      //   this.movePolygonClick(e);
      } else if (this.drawMode || isDrawing) {
        this.handleDrawMove(e);
      } else {
        return;
      }
      canvas.renderAll();
    },

    handleDrawMove: function(e) {
      var pointer = canvas.getPointer(e.e);
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

    loadBB: function(bbox) {
      let rect = new LabeledRect({
        id: bbox.id,
        annoId: bbox.annoId,
        left: bbox.xmin,
        top: bbox.ymin,            
        originX: 'left',
        originY: 'top',
        width: bbox.xmax - bbox.xmin,
        height: bbox.ymax - bbox.ymin,
        angle: 0,
        fill: this.colors[bbox.label],
        transparentCorners: false,
        selectable: false,
        label: bbox.label,
        opacity: 0.3,
        visible: bbox.score >= this.sliderValue,
        score: bbox.score,
        transparentCorners: true,
        cornerSize: this.cornerSize,
        labelType: BOX_LABEL,
        points: bbox.points,
      });
      canvas.add(rect);
    },

    loadPolygon: function(poly) {
      return;
    },

    loadAnnotations: function() {
      let annos = this.image.annotations;
      for (let anno of annos) {
        if (this.exists(anno.bbox)) {
          this.loadBB(anno.bbox)
        }
        if (this.exists(anno.polygon)) {
          this.loadPolygon(anno.polygon)
        }
      }
      canvas.renderAll();
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
      bb.annoId = rect.get('annoId');
      bb.label = rect.get('label');
      bb.score = rect.get('score');
      bb.xmin = coords['tl']['x'],
      bb.ymin = coords['tl']['y'],
      bb.xmax = coords['tr']['x'],
      bb.ymax = coords['br']['y'],
      bb.points = rect.get('points');
      return bb
    },

    extractPolygon: function (obj) {
      let poly = {}
      poly.id = obj.get('id');
      poly.annoId = obj.get('annoId');
      poly.label = obj.get('label');
      poly.score = obj.get('score');
      poly.points = obj.get('points');
      return poly
    },

    getUniqueAnnotationIds: function() {
      let annoIds = new Set();
      let self = this;
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          annoIds.add(o.annoId);
        }
      })
      return annoIds;
    },

    extractAnnotations: function () {
      let annos = [];
      let self = this;
      let annoIdsSet = this.getUniqueAnnotationIds();
      annoIdsSet.forEach(function(id) {
        let anno = self.extractAnnotation(id);
        if (self.exists(anno.bbox) || self.exists(anno.polygon)) {
          annos.push(anno);
        }
      });
      return annos;
    },

    getObjectsByAnnoId: function (annoId) {
      let objs = [];
      let self = this;
      canvas.forEachObject(function(o) {
        console.log("O", o.annoId, o.labelType, annoId);
        if (self.isLabelObject(o) && o.annoId === annoId) {
          objs.push(o);
        }
      })
      console.log("OOO", objs);
      return objs;
    },

    extractAnnotation: function(id) {
      let objs = this.getObjectsByAnnoId(id);
      let anno = {
        'id': id,
        'label': objs[0].label,
      }
      for (let o of objs) {
        if (o.labelType === BOX_LABEL) {
          let bb = this.extractBB(o);
          let width = bb.xmax - bb.xmin;
          let height = bb.ymax - bb.ymin;
          if (width !== 0 && height !== 0 && bb.score >= this.sliderValue) {
            anno['bbox'] = bb;
          }
        } else if (o.labelType === POLYGON_LABEL) {
          let poly = this.extractPolygon(o);
          if (poly.points.length > 2 && poly.score >= this.sliderValue) {
            anno['polygon'] = poly;
          }
        }
      }
      return anno;
    },

    getNextImg: function () {
      this.$apollo.queries.nextObjDetectImage.refetch();
    },

    save: function () {
      let annos = this.extractAnnotations();
      console.log("Saving annos", annos);
      this.$apollo.mutate({
        mutation: SAVE_OBJ_DETECT_IMAGE,
        variables: {
          id: this.image.id,
          project: this.project,
          annotations: annos
        }
      }).then((data) => {
        this.$apollo.queries.nextObjDetectImage.refetch();
      })
    },

    getBoxScore: function(id) {
      let box = null;
    },

    adjustThreshold: function() {
      let self = this;
      const val = this.sliderValue;
      let visible;
      if (canvas !== undefined) {
        canvas.forEachObject(function(o) {
          if (self.isLabelObject(o)) {
            print("WHATTTSUP", o);
            if (o.score >= val) {
              o.visible = true;
            } else {
              o.visible = false;
            }
            // o.visible = (o.score >= val);
          }
        })
        canvas.renderAll();
      }
    },

    isLabelObject: function(obj) {
      return (obj.labelType !== undefined 
              && LABEL_TYPES.indexOf(obj.labelType) !== -1);
    },

    navigateNextBox: function(direction) {
      //print("Navigating " + direction);
      let self = this;
      let curBox = canvas.getActiveObject();
      canvas.discardActiveObject();
      let boxes = [];
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o) && o.score >= self.sliderValue) {
          boxes.push(o);
        }
      })
      this.sortBoxesByProp(boxes, 'left');
      let box;
      for (let i=0; i<boxes.length; i++) {
        box = boxes[i];
        if (box.id === curBox.id) {
          if (direction === 'right') {
            if (i+1 < boxes.length) {
              //console.log("Rightnext", boxes[i+1].id, boxes[i+1].left);
              self.setCurrentObject(boxes[i+1]);
            } else {
              //console.log("Rightfirst", boxes[0].id, boxes[0].left);
              self.setCurrentObject(boxes[0]);
            }
          } else {
            if (i === 0) {
              self.setCurrentObject(boxes[boxes.length-1]);
            } else {
              self.setCurrentObject(boxes[i-1]);
            }
          }
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
      let obj = canvas.getActiveObject();
      if (obj !== undefined && obj !== null) {
        if (obj._objects instanceof Array) {
          if (this.polygonMode) {
            this.resetPolygonMode();
            this.setPolygonMode();
          }
          if (obj._objects.length > 0) {
            for (let i in obj._objects) {
              canvas.remove(obj._objects[i]);
             }
          }
        } else if (this.polygonMode) {
          this.deletePolygonClick(obj);
          return;
        } else {
          canvas.remove(obj);
        }
        canvas.renderAll();
        this.setDefaultObject();
      }
    },

    setDefaultObject: function() {
      if (canvas !== undefined) {
        let boxes = canvas.getObjects();
        this.sortBoxesByProp(boxes, 'left');
        for (let i in boxes) {
          if (this.isLabelObject(boxes[i])) {
            if (boxes[i].score >= this.sliderValue) {
              canvas.setActiveObject(boxes[i]);
              break;
            }
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

    setCornerSize: function(size) {
      let self = this;
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.set({cornerSize: parseFloat(size)});
        }
      })
      canvas.renderAll();
    },

    setDrawMode: function () {
      this.deselectObject();
      isDrawing = true;
      this.drawMode = true;
      let self = this;
      this.resetExtremeClicks();
      this.resetPolygonMode();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.selectable = false;
        }
      }).selection = false;
      canvas.renderAll();
    },

    setSelectMode: function() {
      console.log("ALL Objs", canvas.getObjects());
      isDrawing = false;
      this.drawMode = false;
      let self = this;
      this.resetExtremeClicks();
      this.resetPolygonMode();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          console.log(o);
          o.set({selectable: true}).setCoords();
        }
      }).selection = true;
      let obj = canvas.getActiveObject();
      if (obj === undefined || obj === null) {
        this.setDefaultObject();
      }
      canvas.renderAll();
    },
    
    setExtremeClickMode: function() {
      this.deselectObject();
      this.extremeClickMode = true;
      this.extremeClicks = [];
      let self = this;
      this.resetPolygonMode();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.selectable = false;
        }
      }).selection = false;
      canvas.renderAll();
    },

    setPolygonMode: function() {
      this.deselectObject();
      this.polygonMode = true;
      this.polygonClicks = [];
      let self = this;
      this.resetExtremeClicks();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.selectable = false;
        }
      }).selection = false;
      canvas.renderAll();
    },

    toggleUnselectedVisibility: function(updateToggle) {
      if (updateToggle) {
        //console.log("Updating toggle", this.hideUnselected, !this.hideUnselected);
        this.hideUnselected = !this.hideUnselected;
      } 
      let curBox = canvas.getActiveObject();
      let allBoxes = canvas.getObjects();
      for (let box of allBoxes) {
        if (box.id !== curBox.id) {
          if (box.score < this.sliderValue) {
            box.visible = false;
          } else {
            //console.log("Making visible", !this.hideUnselected);
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
