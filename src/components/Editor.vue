<template>
  <v-app id="example-1" dark>
    <v-navigation-drawer permanent clipped dark :mini-variant="mini">
      <v-list class="pt-0">

        <v-list-tile @click="setSelectMode()" v-tooltip:bottom="{ html: 'Select' }">
          <v-icon large>open_with</v-icon>
        </v-list-tile>
        <v-list-tile @click="setDrawMode()" v-tooltip:bottom="{ html: 'Draw box' }">
          <v-icon large>crop_free</v-icon>
        </v-list-tile>
        <v-list-tile @click="setExtremeClickMode()" v-tooltip:bottom="{ html: 'Click box' }">
          <v-icon large>filter_center_focus</v-icon>
        </v-list-tile>
        <v-list-tile @click="setPolygonMode()" v-tooltip:bottom="{ html: 'Polygon' }">
          <v-icon large>mode_edit</v-icon>
        </v-list-tile>
        <v-list-tile @click="toggleUnselectedVisibility(true)" v-tooltip:bottom="{ html: 'Hide mode' }">
          <v-icon large>layers</v-icon>
        </v-list-tile>
        <v-list-tile @click="setZoomMode()" v-tooltip:bottom="{ html: 'Zoom mode' }">
          <v-icon large>zoom_in</v-icon>
        </v-list-tile>
        <!-- <v-list-tile @click="resetZoom()" v-tooltip:bottom="{ html: 'Reset zoom' }">
          <v-icon large>zoom_out</v-icon>
        </v-list-tile> -->
        <v-list-tile @click="deleteObject()" v-tooltip:bottom="{ html: 'Delete' }">
          <v-icon large>delete</v-icon>
        </v-list-tile>
        <v-list-tile to="/" v-tooltip:bottom="{ html: 'Help' }">
          <v-icon large>help_outline</v-icon>
        </v-list-tile>
        <v-list-tile @click="" v-tooltip:bottom="{ html: 'Shortcuts' }">
          <v-bottom-sheet v-model="shortcutSheet">
          <v-icon slot="activator" large>keyboard</v-icon>
          <v-list two-line subheader>
            <v-list-tile avatar v-for="shortcut in shortcuts" v-if="shortcut.desc !== null" :key="shortcut.key">
              <v-list-tile-content>
                <v-list-tile-title>{{shortcut.desc}}</v-list-tile-title>
                <v-list-tile-sub-title>{{shortcut.key}}</v-list-tile-sub-title>
              </v-list-tile-content>
            </v-list-tile>
          </v-list>
          </v-bottom-sheet>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar fixed class="darken-2" dark>
    <v-btn icon to="/">
      <v-icon>arrow_back</v-icon>
    </v-btn>
      <v-toolbar-title>My Project</v-toolbar-title>
      <v-spacer></v-spacer>

      <v-flex xs3 sm3>
        <v-slider
        label="Accelerate:"
        v-on="adjustThreshold()"
        v-model="sliderValue"
        :step="5" 
        snap 
        thumb-label
        dark>
        </v-slider>
      </v-flex>

      <v-flex xs3 sm3>
        <v-select id='select-label'
          prepend-icon="label"
          v-bind:items="labels"
          v-model="selectedLabel"
          label="Select label"
          return-object
          :autocomplete="autocompleteLabels"
        ></v-select>
      </v-flex>

    <v-btn icon @click="prevImage()" v-tooltip:bottom="{ html: 'Previous image' }">
      <v-icon large>navigate_before</v-icon>
    </v-btn>
    <v-btn icon @click="nextImage()" v-tooltip:bottom="{ html: 'Next image' }">
      <v-icon large>navigate_next</v-icon>
    </v-btn>
    <v-btn icon @click="save()" v-tooltip:bottom="{ html: 'Save annotations' }">
      <v-icon large>save</v-icon>
    </v-btn>
    <v-btn icon>
      <v-icon large>more_vert</v-icon>
    </v-btn>    
    </v-toolbar>

    <main>
      <v-container fluid>
        <canvas id="c"></canvas>
      </v-container>
    </main>

    <v-footer dark>
      <span class="white--text">© 2017</span>
    </v-footer>
  </v-app>
  
</template>

<script>
import {fabric} from 'fabric'
import RangeSlider from 'vue-range-slider'

import keys from '../constants/keyboard.js';

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
  let moveKeys = ['up','down','right','left'];
  let code = e.keyCode;
  let keyObj = keys.KEY_MAP[code];
  let key;
  if (keyObj === null || keyObj === undefined) {
    key = null;
  } else {
    key = keyObj.key;
  }
  let obj = canvas.getActiveObject();
  if (e.shiftKey || e.ctrlKey || e.altKey || e.keyCode === 9) {
    e.preventDefault();
    e.stopImmediatePropagation()
  }
  
  // Shrink box
  if (key === 'left' && e.shiftKey && e.altKey) {
    obj.set({width: obj.width -= 5});
  } else if (key === 'right' && e.shiftKey && e.altKey) {
    obj.set({width: obj.width -= 5})
    obj.set({left: obj.left += 5});
  } else if (key === 'up' && e.shiftKey && e.altKey) {
    obj.set({height: obj.height -= 5});
  } else if (key === 'down' && e.shiftKey && e.altKey) {
    obj.set({height: obj.height -= 5})
    obj.set({top: obj.top += 5});

  // Stretch box
  } else if (key === 'left' && e.shiftKey) {
    obj.set({width: obj.width += 5})
    obj.set({left: obj.left -= 5});
  } else if (key === 'right' && e.shiftKey) {
    obj.set({width: obj.width += 5});
  } else if (key === 'up' && e.shiftKey) {
    obj.set({height: obj.height += 5})
    obj.set({top: obj.top -= 5});
  } else if (key === 'down' && e.shiftKey) {
    obj.set({height: obj.height += 5});
  
  // Move Box
  } else if (key === 'left') {
    obj.set({left: obj.left -= 5});
  } else if (key === 'right') {
    obj.set({left: obj.left += 5});
  } else if (key === 'up') {
    obj.set({top: obj.top -= 5});
  } else if (key === 'down') {
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
        ctx.font = '14px Helvetica';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(text, -this.width/2, -this.height/2 + 8);
    }
});


var canvas;
var drawRect, origX, origY;

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
      selectedLabel: null,
      sliderValue: 100,
      clickRadius: 4,
      cornerSize: 7,
      extremeClickRadius: 4,
      polyClickRadius: 4,
      hideUnselected: false,
      selectMode: true,
      drawMode: false,
      extremeClickMode: false,
      extremeClicks: [],
      polygonMode: false,
      polygonClicks: [],
      labels: [],
      colors: {},
      rects: [],
      zoomFactor: 1,
      grabMode: false,
      zoomMode: false,
      maxZoom: 10,
      minZoom: .25,
      drawer: null,
      mini: true,
      shortcutSheet: false,
      shortcuts: keys.KEYS,
      shortcutHeaders: ['key', 'description'],
      tiles: [
        { img: 'keep.png', title: 'Keep' },
        { img: 'inbox.png', title: 'Inbox' },
        { img: 'hangouts.png', title: 'Hangouts' },
        { img: 'messenger.png', title: 'Messenger' },
        { img: 'google.png', title: 'Google+' },
      ]
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
        this.selectedLabel = this.labels[0];
        this.initializeCanvas();
        this.loadAnnotations();
      },
    },
  },
  
  computed: {
      autocompleteLabels: function () {
        return false;
    },
  },

  filters: {
    capitalize: function (value) {
      if (!value) return ''
      value = value.toString()
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
  },

  mounted: function() {
    return
  },

  created: function () {
    let self = this;
    window.addEventListener('keyup', function(e) {
      let moveKeys = ['up','down','right','left'];
      let code = e.keyCode;
      let keyObj = keys.KEY_MAP[code];
      let key;
      if (!self.exists(keyObj)) {
        key = null;
      } else {
        key = keyObj.key;
      }
      console.log("Key", e.keyCode);
      if (key === 's' && e.ctrlKey) {
        self.save();
      } else if (key === 'z' && e.ctrlKey) {
        self.setZoomMode();
      } else if (key === 'c' && e.ctrlKey) {
        self.setExtremeClickMode();
      } else if (key === 'p' && e.ctrlKey) {
        self.setPolygonMode();
      } else if (key === 'n' && e.ctrlKey) {
        self.nextImage();
      } else if (key === 'a' && e.ctrlKey) {
        self.setSelectMode();
      } else if (key === 'd' && e.ctrlKey) {
        self.setDrawMode();
      } else if (key === 'h' && e.ctrlKey) {
        self.toggleUnselectedVisibility(true);
      } else if (key === 'tab' && e.shiftKey) {
        self.navigateNextBox('left');
      } else if (key === 'tab') {
        self.navigateNextBox('right');
      } else if (key === 'esc') {
        self.deselectObject();
      } else if (key === 'delete' || key === 'backspace') {
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
        self.width = this.width;
        self.height = this.height;
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
        'mouse:dblclick': this.mouseDblClickHandler,
        'mouse:down': this.mouseDownHandler,
        'mouse:up': this.mouseUpHandler,
        'mouse:move': this.mouseMoveHandler,
        'object:moving': this.objectMovingHandler,
        'mouse:over': this.mouseOverHandler,
        'mouse:out': this.mouseOutHandler,
        'mouse:wheel': this.mouseWheelHandler,
      });
      this.setSelectMode();
      canvas.renderAll();
    },

    objectOverHandler: function(e) {
      console.log("object over");
      if (this.extremeClickMode) {
        canvas.defaultCursor = 'default';
      }
      return;
    },

    objectMovingHandler: function(e) {
      if (this.extremeClickMode) {
        return;
      } else if (this.polygonMode) {
        this.adjustPolygonClick(e);
      } else if (this.drawMode) {
        this.handleDrawMove(e);
      } else {
        return;
      }
    },

    mouseOverHandler: function(e) {
      //console.log("object over");
      if (this.extremeClickMode) {
        // canvas.hoverCursor = 'pointer';
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
      console.log("Mouse down", e);
      console.log("T", e.target);
      if (this.extremeClickMode) {
        this.initExtremeClick(e);
      } else if (this.polygonMode) {
        this.initPolygon(e);
      } else if (this.drawMode) {
        this.makeRectangle(e);
      } else if (this.zoomMode) {
        this.zoomToClick(e);
      } else if (e.target === null) {
        console.log("setting grab mode");
        this.setGrabMode();
      }
    },

    mouseUpHandler: function(e) {
      console.log("Mouse up", this.sliderValue);
      if (this.grabMode) {
        this.exitGrabMode();
      } else if (this.extremeClickMode) {
        this.saveExtremeClick(e);
      } else if (this.polygonMode) {
        this.handlePolygonClick(e);        
      } else if (this.drawMode) {
        console.log("draw mode mouse up");
        this.saveRectangle(e);
      } else {
        return;
      }
      canvas.renderAll();
    },

    mouseMoveHandler: function(e) {
      if (this.grabMode) {
        console.log("handling grab move")
        this.handleGrabMove(e);
      } else if (this.drawMode) {
        this.handleDrawMove(e);
      } else {
        return;
      }
      canvas.renderAll();
    },

    mouseWheelHandler: function(e) {
      console.log("Mouse wheel", e.e.target);
      if (this.zoomMode) {
        this.zoomToPoint(e);
      }
    },

    mouseDblClickHandler: function(e) {
      console.log("Mouse dblclick", e.e.target);
      if (this.extremeClickMode && e.target !== null) {
        this.resetExtremeClicks();
        this.setSelectMode();
        this.deselectObject();
        canvas.setActiveObject(e.target);
      } else if (this.polygonMode) {
        return;
      } else if (this.drawMode) {
        print("Draw mode dbl click");
        return;
      } else {
        return;
      }
    },

    makeRectangle: function(e) {
      var pointer = canvas.getPointer(e.e);
      origX = pointer.x;
      origY = pointer.y;
      var pointer = canvas.getPointer(e.e);
      let rect = new LabeledRect({
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
      drawRect = rect;
      canvas.renderAll();
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
      console.log('init extreme click');
      if (e.target !== null) {
        console.log("found target");
      }
    },

    initPolygon: function(e) {
      console.log('init polygon click', canvas.getActiveObject());
      
    },

    saveRectangle: function(e) {
      console.log('saving rectangle', this.selectedLabel);
      console.log(drawRect);
      drawRect.set({
        score: 1.0
      });
      drawRect.setCoords();
      drawRect.selectable = false;
      // let copy = fabric.util.object.clone(drawRect);
      // canvas.remove(drawRect);
      // canvas.add(drawRect);
      drawRect = null;
      canvas.renderAll();
      //this.setSelectMode();

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
          padding: 5,
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
      polygon.selectable = false;
      canvas.add(polygon);
      // Update labels.json
      this.exitPolygonMode();
      this.setPolygonMode();
      // canvas.setActiveObject(polygon);
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
          && this.polygonClicks.length > 0) {
        if (obj === this.polygonClicks[0]) {
          obj.set({
            stroke: 'green',
            fill: 'green',
          });
        } else if (obj.selectable === true) {
          console.log("OBJ SELECTABLE")
          canvas.hoverCursor = 'move';
        }
      }
      canvas.renderAll();
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
        'id': this.getRandId(),
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
      r = this.createRectFromCoords(xmin, ymin, xmax, ymax);
      r.points = points;
      this.removeExtremeClicks();
    },

    removeExtremeClicks: function() {
      while (this.extremeClicks.length > 0){
        this.removeObjectById(this.extremeClicks[0]);
        this.extremeClicks.splice(0, 1);
      }
    },

    resetExtremeClicks: function() {
      this.removeExtremeClicks();
      this.extremeClickMode = false;
      print(this.image);
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

    exitPolygonMode: function() {
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
      rect.selectable = false;
      canvas.add(rect);
      canvas.renderAll();
      return rect;
    },

    handleGrabMove: function(e) {
      console.log("handling grab move", e.e);
      var delta = new fabric.Point(e.e.movementX, e.e.movementY) ;
      canvas.relativePan(delta);
    },

    handleDrawMove: function(e) {
      if (!this.exists(drawRect)) {
        return;
      }
      let pointer = canvas.getPointer(e.e);
      if (origX > pointer.x) {
        drawRect.set({
          left: Math.abs(pointer.x)
        });
      }
      if (origY > pointer.y) {
        drawRect.set({
          top: Math.abs(pointer.y)
        });
      }
      drawRect.set({
        width: Math.abs(origX - pointer.x)
      });
      drawRect.set({
        height: Math.abs(origY - pointer.y)
      });
    },

    loadBB: function(bbox) {
      console.log("slider",this.sliderValue/100);
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
        visible: bbox.score >= (this.sliderValue/100),
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
      console.log("GETTING LABEL COLOR", label);
      console.log("GETTING LABEL COLOR", this.colors[label]);
      return this.colors[label];
    },

    getCurLabel: function () {
      console.log("SELECTED", this.selectedLabel);
      return this.selectedLabel.value;
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
      //Update to make sure coord is less than width/height of picture
      let bb = {}
      let coords = rect.get('aCoords');
      bb.id = rect.get('id');
      bb.annoId = rect.get('annoId');
      bb.label = rect.get('label');
      bb.score = rect.get('score');
      bb.xmin = Math.min(Math.max(coords['tl']['x'],0),this.width),
      bb.ymin = Math.min(Math.max(coords['tl']['y'],0),this.height),
      bb.xmax = Math.min(Math.max(coords['tr']['x'],0),this.width),
      bb.ymax = Math.min(Math.max(coords['br']['y'],0),this.height),
      bb.points = rect.get('points');
      console.log("Extracting", bb);
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
          if (width !== 0 && height !== 0 && bb.score >= this.sliderValue/100) {
            anno['bbox'] = bb;
          }
        } else if (o.labelType === POLYGON_LABEL) {
          let poly = this.extractPolygon(o);
          if (poly.points.length > 2 && poly.score >= this.sliderValue/100) {
            anno['polygon'] = poly;
          }
        }
      }
      return anno;
    },

    nextImage: function () {
      this.$apollo.queries.nextObjDetectImage.refetch();
    },

    prevImage: function () {
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
      const val = this.sliderValue/100;
      console.log("VALUE", val);
      let visible;
      if (canvas !== undefined) {
        canvas.forEachObject(function(o) {
          if (self.isLabelObject(o)) {
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
        if (self.isLabelObject(o) && o.score >= self.sliderValue/100) {
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
            this.exitPolygonMode();
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
        this.setSelectMode();
      }
    },

    setDefaultObject: function() {
      let box;
      if (canvas !== undefined) {
        let boxes = canvas.getObjects();
        this.sortBoxesByProp(boxes, 'left');
        for (let i in boxes) {
          if (this.isLabelObject(boxes[i])) {
            if (boxes[i].score >= this.sliderValue/100) {
              canvas.setActiveObject(boxes[i]);
              canvas.renderAll();
              return boxes[i];
            }
          }
        }

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

    setCursors: function() {
      if (this.extremeClickMode || this.polygonMode || this.drawMode) {
        canvas.defaultCursor = 'pointer';
        canvas.hoverCursor = 'pointer';
      } else if (this.zoomMode) {
        canvas.defaultCursor = 'zoom-in';
        canvas.hoverCursor = 'zoom-in';
      } else {
        canvas.defaultCursor = 'default';
        canvas.hoverCursor = 'move';
      }
      canvas.renderAll();
    },

    setZoomMode: function(e) {
      console.log("Setting zoom mode");
      this.zoomMode = true;
      this.exitDrawMode();
      this.exitPolygonMode();
      this.resetExtremeClicks();
      this.setCursors();
    },

    exitZoomMode: function() {
      this.zoomMode = false;
      this.setCursors();
      this.exitGrabMode();
    },

    scalePoints: function(delta) {
      console.log("scaling points by", this.zoomFactor, this.extremeClickRadius, this.polyClickRadius);
      this.clickRadius = Math.min(Math.max(this.clickRadius * delta, 1), 10);
      this.cornerSize = Math.min(Math.max(this.cornerSize * delta, 1), 10);
      this.extremeClickRadius = Math.min(Math.max(this.extremeClickRadius * delta, 1), 10);
      this.polyClickRadius = Math.min(Math.max(this.polyClickRadius * delta, 1), 10);
      let self = this;
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          if (o.labelType === POLY_CLICK_LABEL) {
            o.radius = self.polyClickRadius;
          } else if (o.labelType === EC_LABEL) {
            o.radius = self.extremeClickRadius;
          }
        }
      })
      canvas.renderAll();
    },

    resetZoom: function() {
      this.zoomFactor = 1 ;
      console.log(canvas.width, canvas.height);
      canvas.setZoom(this.zoomFactor);
      canvas.zoomToPoint(new fabric.Point(
        canvas.width/2, canvas.height/2), this.zoomFactor);
    },

    zoomToClick: function(e) {
      let pointer = canvas.getPointer(e.e);
      console.log("ZP", e);
      let cursor, delta;
      if (e.e.shiftKey) {
        cursor = 'zoom-out';
        delta = .95;
      } else {
        cursor = 'zoom-in';
        delta = 1.1;
      }
      this.zoomFactor *= delta;
      canvas.zoomToPoint(new fabric.Point(
        e.e.offsetX, e.e.offsetY), this.zoomFactor);
    },

    zoomToPoint: function(e) {
      console.log("zooming to point", e, e.target);
      let pointer = canvas.getPointer(e.e);
      console.log("WD", e.e.wheelDelta);
      let zoomIn = e.e.wheelDelta < 0;
      let curZoom = this.zoomFactor;
      let cursor, delta;
      if (zoomIn) {
        cursor = 'zoom-in';
        delta = 1.1;
        //this.scalePoints(.95);
      } else {
        cursor = 'zoom-out';
        delta = .95
        //this.scalePoints(1.1);
      }
      this.zoomFactor *= delta;
      console.log(cursor);
      // canvas.defaultCursor = cursor;
      // canvas.hoverCursor = cursor;
      canvas.zoomToPoint(new fabric.Point(
        e.e.offsetX, e.e.offsetY), this.zoomFactor);
      //this.resetCursors();
// let obj = e.target;
      // if (obj !== undefined 
      //     && obj !== null
      //     && this.polygonClicks.length > 0
      //     && obj === this.polygonClicks[0]) {
      //   obj.set({
      //     stroke: 'green',
      //     fill: 'green',
      //   });
      //   canvas.renderAll();
      // }
    },

    setDrawMode: function () {
      this.deselectObject();
      this.drawMode = true;
      let self = this;
      this.exitGrabMode();
      this.exitZoomMode();
      this.resetExtremeClicks();
      this.exitPolygonMode();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.selectable = false;
        }
      }).selection = false;
      canvas.renderAll();
    },

    exitDrawMode: function() {
      this.deselectObject();
      this.drawMode = false;
    },

    setSelectMode: function() {
      console.log("S ALL Objs", canvas.getObjects());
      let self = this;
      this.exitZoomMode();
      this.exitDrawMode();
      this.resetExtremeClicks();
      this.exitPolygonMode();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          console.log(o);
          o.set({selectable: true}).setCoords();
        }
      });
      let obj = canvas.getActiveObject();
      if (obj === undefined || obj === null) {
        this.setDefaultObject();
      }
      canvas.defaultCursor = 'default';
      canvas.hoverCursor = 'move';
      canvas.renderAll();
    },
    
    setExtremeClickMode: function() {
      this.deselectObject();
      this.extremeClickMode = true;
      this.extremeClicks = [];
      let self = this;
      this.exitZoomMode();
      this.exitGrabMode();
      this.exitDrawMode();
      this.exitPolygonMode();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.selectable = false;
        }
      }).selection = false;
      canvas.defaultCursor = 'pointer';
      canvas.hoverCursor = 'pointer';
      canvas.renderAll();
    },

    setPolygonMode: function() {
      this.deselectObject();
      this.polygonMode = true;
      this.polygonClicks = [];
      let self = this;
      this.exitZoomMode();
      this.exitGrabMode();
      this.exitDrawMode();
      this.resetExtremeClicks();
      canvas.forEachObject(function(o) {
        if (self.isLabelObject(o)) {
          o.selectable = false;
        }
      }).selection = false;
      canvas.renderAll();
    },

    setGrabMode: function(e) {
      this.grabMode = true;
      canvas.defaultCursor = 'move';
      canvas.renderAll();
    },

    exitGrabMode: function() {
      this.grabMode = false;
      this.setCursors();
    },

    toggleUnselectedVisibility: function(updateToggle) {
      if (updateToggle !== undefined && updateToggle) {
        //console.log("Updating toggle", this.hideUnselected, !this.hideUnselected);
        this.hideUnselected = !this.hideUnselected;
      }
      let curBox = canvas.getActiveObject();
      if (!this.exists(curBox)) {
        curBox = this.setDefaultObject();
      }
      let allBoxes = canvas.getObjects();
      for (let box of allBoxes) {
        if (box.id !== curBox.id) {
          if (box.score < this.sliderValue/100) {
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
