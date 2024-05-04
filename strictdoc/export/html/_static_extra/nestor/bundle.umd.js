(function(c,_){typeof exports=="object"&&typeof module<"u"?module.exports=_():typeof define=="function"&&define.amd?define(_):(c=typeof globalThis<"u"?globalThis:c||self,c.GraphNestor=_())})(this,function(){"use strict";var C=Object.defineProperty;var N=(c,_,f)=>_ in c?C(c,_,{enumerable:!0,configurable:!0,writable:!0,value:f}):c[_]=f;var g=(c,_,f)=>(N(c,typeof _!="symbol"?_+"":_,f),f);class c{constructor(t){this.text=t}add(t){const e=document.querySelector("head"),s=document.body;if(!e&&!s){console.error("Check the structure of your document. We didn`t find HEAD and BODY tags. HTML2PDF4DOC expects valid HTML.");return}const i=document.createElement("style");i.setAttribute("graph-nestor-styles","css"),i.innerHTML=t||this.text,e?e.append(i):s?s.before(i):console.assert(!1,"We expected to find the HEAD and BODY tags.")}}class _{constructor({background:t,color:e,preloaderClass:s,fadeTime:i}={}){this._preloader,this._preloaderFadeTime=i||50,this._preloaderContainer,this._contentContainer,this._background=t||"transparent",this._color=e||"orangered",this._preloaderClass=s||"lds-dual-ring",this._css=`
    /* PRELOADER */
    .${this._preloaderClass} {
      position: absolute;
      z-index: 99999;
      top: 0; left: 0; bottom: 0; right: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      background: ${this._background};
    }
    .${this._preloaderClass}:after {
      content: " ";
      display: block;
      width: 64px;
      height: 64px;
      margin: 8px;
      border-radius: 50%;
      border: 6px solid ${this._color};
      border-color: ${this._color} ${this._background} ${this._color} ${this._background};
      animation: ${this._preloaderClass} 1.2s linear infinite;
    }
    @keyframes ${this._preloaderClass} {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }
    `}add({preloaderContainer:t,contentContainer:e}){new c(this._css).add(),this._preloaderContainer=t,this._contentContainer=e,this._create(),this._contentContainer.style.opacity=0}remove(){if(!this._preloader)return;let t=1;const e=setInterval(()=>{t<=.1&&(clearInterval(e),this._preloader.remove(),this._contentContainer.style.opacity=1),this._preloader.style.opacity=t,this._contentContainer.style.opacity=1-t,t-=t*.1},this._preloaderFadeTime)}_create(){this._preloader=document.createElement("div"),this._preloader.classList.add("nestor-preloader"),this._preloader.innerHTML=`<div class="${this._preloaderClass}"></div>`,this._preloaderContainer.append(this._preloader)}}class f{constructor({content:t,initScale:e,minScale:s,maxScale:i,initScaleSpeed:n,initMoveSpeed:o,baseSize:a}){this._canvas,this._container,this._content=t,this._contentClass="nestor-tree",this._baseSize=a||16,this._listeners={},this._css=`
    html, body {
      min-height: 100vh;
      min-width: 100vw;
      height: 100vh;
      width: 100vw;
    }
    .nestor-canvas {
      box-sizing: border-box;
      height: 100%;
      width: 100%;
      max-height: 100vh;
      max-width: 100vw;
      overflow: hidden;
      position: relative;
    }
    .nestor-preloader {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      right: 0;
      pointer-events: none;
      z-index: 10;
    }
    .nestor-container {
      position: absolute;
      left: 0;
      top: 0;
      transform-origin: 0 0;
      pointer-events: none;
    }
    .nestor-container > * {
      pointer-events: all;
    }
    .nestor-control {
      position: absolute;
      right: ${this._baseSize/2}px;
      top: ${this._baseSize/2}px;
      pointer-events: all;
    }
    .nestor-control-button {
      width: ${this._baseSize}px;
      height: ${this._baseSize}px;
      background: red;
    }
    .${this._contentClass} {
      display: flex;
      gap: ${this._baseSize}px;
      padding: ${this._baseSize}px;
      position: relative;
      width: fit-content;
    }
    `,this._scale=e||1,this._scaleMin=s||.25,this._scaleMax=i||2,this._scaleSpeed=n||.001,this._moveSpeed=o||1e3,this._x=0,this._y=0,this._isSpacePressed=!1,this._mouseDown=!1,this._isCtrlPressed=!1,this._isShiftPressed=!1,this._style=new c(this._css),this._preloader=new _({fadeTime:20}),this._init()}get scale(){return this._scale}move(t,e){const s=-t*this._scale+window.innerWidth/2,i=-e*this._scale+window.innerHeight/2;this._moveElement(s,i)}addEventListener(t,e){this._listeners[t]||(this._listeners[t]=[]),this._listeners[t].push(e)}_init(){this._content.classList.add(this._contentClass),this._style.add(),this._createCanvas(),this._initEventListeners(),this._fitContent()}_createCanvas(){this._canvas=document.createElement("div"),this._canvas.classList.add("nestor-canvas"),this._container=document.createElement("div"),this._container.classList.add("nestor-container"),this._content.before(this._canvas),this._canvas.append(this._container),this._container.append(this._content);const t=document.createElement("div");t.classList.add("nestor-control");const e=document.createElement("button");e.classList.add("nestor-control-button"),this._canvas.append(t),t.append(e)}addPreloader(){this._preloader.add({preloaderContainer:this._canvas,contentContainer:this._container})}removePreloader(){this._preloader.remove()}_fitContent(t=0,e=0){this._x=t,this._y=e;const s=this._canvas.offsetWidth/this._container.offsetWidth||1,i=this._canvas.offsetHeight/this._container.offsetHeight||1;this._scale=Math.min(s,i),this._scale=this._scale>1?1:this._scale,this._updateTransform()}_initEventListeners(){this._canvas.addEventListener("wheel",this._handleWheel.bind(this)),this._canvas.addEventListener("mousedown",this._handleMouseDown.bind(this)),this._canvas.addEventListener("mouseup",this._handleMouseUp.bind(this)),this._canvas.addEventListener("mouseleave",this._handleMouseLeave.bind(this)),document.addEventListener("keydown",this._handleKeyDown.bind(this)),document.addEventListener("keyup",this._handleKeyUp.bind(this))}_handleWheel(t){if(t.preventDefault(),this._isCtrlPressed){const e=this._container.getBoundingClientRect(),s=t.clientX-e.left,i=t.clientY-e.top,n=this._scale;this._scale+=t.deltaY*-1*this._scaleSpeed,this._scale=Math.min(Math.max(this._scaleMin,this._scale),this._scaleMax),this._x-=s/n*(this._scale-n),this._y-=i/n*(this._scale-n)}else this._isShiftPressed?this._x+=t.deltaX||t.deltaY:this._y-=t.deltaY;this._updateTransform()}_handleMouseDown(t){this._isSpacePressed&&(t.preventDefault(),this._mouseDown=!0,this.startX=t.clientX-this._x,this.startY=t.clientY-this._y,this._canvas.style.cursor="grabbing",this._canvas.addEventListener("mousemove",this._handleMouseMove.bind(this)))}_handleMouseMove(t){this._mouseDown&&(this._x=t.clientX-this.startX,this._y=t.clientY-this.startY,this._updateTransform())}_handleMouseUp(){this._mouseDown&&(this._mouseDown=!1,this._canvas.style.cursor="grab",this._canvas.removeEventListener("mousemove",this._handleMouseMove))}_handleMouseLeave(){this._mouseDown&&(this._mouseDown=!1,this._canvas.style.cursor="grab",this._canvas.removeEventListener("mousemove",this._handleMouseMove))}_handleKeyDown(t){t.code==="Space"&&!this._isSpacePressed&&(this._isSpacePressed=!0,this._canvas.style.cursor="grab"),(t.key==="Control"||t.key==="Meta")&&(this._isCtrlPressed=!0),t.key==="Shift"&&(this._isShiftPressed=!0)}_handleKeyUp(t){t.code==="Space"&&(this._isSpacePressed=!1,this._canvas.style.cursor="default"),(t.key==="Control"||t.key==="Meta")&&(this._isCtrlPressed=!1),t.key==="Shift"&&(this._isShiftPressed=!1)}_updateTransform(){this._container.style.transform=`translate(${this._x}px, ${this._y}px) scale(${this._scale})`,this._dispatchEvent("scaleChange",this._scale)}_moveElement(t,e){let s=null;const i=n=>{s||(s=n);const o=Math.min((n-s)/this._moveSpeed,1);this._x=this._x+o*(t-this._x),this._y=this._y+o*(e-this._y),this._updateTransform(),o<1&&requestAnimationFrame(i)};requestAnimationFrame(i)}_dispatchEvent(t,e){this._listeners[t]&&this._listeners[t].forEach(s=>s(e))}}class v{constructor({baseSize:t,cssClass:e}={}){this._nestClass=e||"nestor-nest",this._baseSize=t||16,this._css=`
    .${this._nestClass} {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: ${this._baseSize}px;
      height: fit-content;
      /* BOX */
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(0,0,0,0.2);
      border-radius: 8px;
      box-shadow: 0 0 8px rgba(0,0,0,0);
      padding: ${this._baseSize}px;
      /* TEXT */
      font-family: sans-serif;
      /* *** */
      transition: box-shadow .3s;
    }
    .${this._nestClass}:hover {
      box-shadow: 0 0 ${this._baseSize/2}px rgba(0,0,0,0.5);
    }
    `,this._init()}_init(){new c(this._css).add()}create(t){const e=document.createElement("div");return e.classList.add(this._nestClass),typeof t=="string"?e.innerHTML=t:t instanceof HTMLElement&&e.append(t),e}}class x{constructor({baseSize:t,key:e={mid:"mid",title:"title",uid:"uid",type:"type"},cssClass:s=["nestor-node","nestor-node-box_main","nestor-node-box_left","nestor-node-box_right","nestor-node-box_top","nestor-node-box_bottom","nestor-node-title","nestor-node-uid","nestor-node_field","nestor-node_field-title","nestor-node_field-value","nestor-node-relation-point"]}={}){this._key={type:e.type,title:e.title,uid:e.uid,mid:e.mid,relations:e.relations},this._nodeClass=s[0],this._nodeBoxMainClass=s[1],this._nodeBoxLeftClass=s[2],this._nodeBoxRightClass=s[3],this._nodeBoxTopClass=s[4],this._nodeBoxBottomClass=s[5],this._nodeTitleClass=s[6],this._nodeUIDClass=s[7],this._fieldClass=s[8],this._fieldTitleClass=s[9],this._fieldValueClass=s[10],this._relationPointClass=s[11],this._baseSize=t||16,this._css=`
      .${this._nodeClass} {
        display: grid;
        grid-template-areas:
          ".    top    ."
          "left main   right"
          ".    bottom .";
        grid-template-columns:
          minmax(0, max-content) minmax(min-content, max-content) minmax(0, max-content);
        grid-template-rows:
          minmax(0, max-content) minmax(min-content, max-content) minmax(0, max-content);
        /* BOX */
        background: white;
        border-radius: 8px;
        min-width: 111px;
        max-width: 333px;
        width: fit-content;
      }
      .${this._nodeBoxTopClass},
      .${this._nodeBoxBottomClass},
      .${this._nodeBoxRightClass},
      .${this._nodeBoxLeftClass} {
        display: flex;
        gap: ${this._baseSize*1.25}px;
        justify-content: center;
        align-items: center;
      }
      .${this._nodeBoxTopClass} {
        flex-direction: row;
        grid-area: top;
        padding: 0 ${this._baseSize*1.25}px;
      }
      .${this._nodeBoxBottomClass} {
        flex-direction: row;
        grid-area: bottom;
        padding: 0 ${this._baseSize*1.25}px;
      }
      .${this._nodeBoxLeftClass} {
        flex-direction: column;
        grid-area: left;
        padding: ${this._baseSize*1.25}px 0;
      }
      .${this._nodeBoxRightClass} {
        flex-direction: column;
        grid-area: right;
        padding: ${this._baseSize*1.25}px 0;
      }
      .${this._relationPointClass} {
        position: relative;
        z-index: 3;
      }
      .${this._relationPointClass}::after {
        content: '';
        position: absolute;
        z-index: 3;
        border-radius: 50%;
        transition: all .3s;
        background: black;
        box-sizing: border-box;
        width: ${this._baseSize}px;
        height: ${this._baseSize}px;
        outline: ${this._baseSize*.25}px solid white;
        border: ${this._baseSize*.125}px solid white;
        top: ${-.5*this._baseSize}px;
        left: ${-.5*this._baseSize}px;
      }
      .${this._relationPointClass}:hover {
        cursor: pointer;
        z-index: 4;
      }
      .${this._relationPointClass}[active]::after {
        background: orange;
      }
      .${this._relationPointClass}[active]:hover::before {
        content: '';
        position: absolute;
        z-index: 5;
        border-radius: 50%;
        transition: all .3s;
        box-sizing: border-box;
        width: ${1.4*this._baseSize}px;
        height: ${1.4*this._baseSize}px;
        top: ${-.7*this._baseSize}px;
        left: ${-.7*this._baseSize}px;
        border: 1px dashed black;
      }
      .${this._relationPointClass}:hover::after {
        background: orange;
        outline: ${this._baseSize*.5}px solid white;
      }
      .${this._relationPointClass}[point="source"]::after {
        border-width: ${this._baseSize*.125}px;
      }
      .${this._relationPointClass}[point="target"]::after {
        border-width: ${this._baseSize*.25}px;
      }
      .${this._nodeBoxMainClass} {
        grid-area: main;
        display: grid;
        grid-template-columns: minmax(min-content, max-content) minmax(min-content, max-content);
        align-items: baseline;
        gap: ${this._baseSize*.5}px;
        /* BOX */
        background: white;
        padding: ${this._baseSize*1.75}px ${this._baseSize*1}px ${this._baseSize*.75}px;
        border-radius: ${this._baseSize*.5}px;
        min-width: 111px;
        max-width: 333px;
        /* TEXT */
        font-family: sans-serif;
        /* for ::before */
        position: relative;
      }
      .${this._nodeBoxMainClass}::before {
        content: attr(type);
        position: absolute;
        z-index: 10;
        top: ${this._baseSize/2}px;
        right: ${this._baseSize/2}px;
        font-size: xx-small;
        line-height: 1;
        font-weight: bold;
      }
      .${this._nodeBoxMainClass}[type="SECTION"]::before{
        color: green
      }
      .${this._nodeBoxMainClass}[type="REQUIREMENT"]::before{
        color: blue
      }
      .${this._nodeTitleClass} {
        grid-column: 1 / -1;
        font-weight: bold;
      }
      .${this._nodeUIDClass} {
        grid-column: 1 / -1;
        max-width: max-content;
        font-size: x-small;
        font-weight: bold;
        padding: ${this._baseSize/8}px ${this._baseSize/4}px;
        border-radius: ${this._baseSize/4}px;
        background: rgba(0,0,0,0.1)
      }
      .${this._fieldClass} {
        display: contents;
      }
      .${this._fieldTitleClass} {
        font-size: small;
        text-transform: capitalize;
        font-weight: bold;
      }
      .${this._fieldValueClass} {
        max-width: 222px;
        word-break: break-word;
      }
    `,this._init()}_init(){new c(this._css).add()}create(t={test:"test"}){const{node:e,nodeMain:s}=this._createNodeBox();return this._setType(s,t),this._setUID(s,t),this._setUID(e,t),this._setMID(s,t),Object.entries(this._getSelectedFields(t)).map(([i,n])=>{n&&s.append(this._createField(i,n))}),e}createRelationPoint(t,e,s,i,n){const o=t.querySelector(`[bus='${s}']`),a=document.createElement("div");return a.classList.add(this._relationPointClass),a.style.order=e.offsetTop,i&&a.setAttribute("point",i),n&&a.setAttribute("relation",n),o.append(a),a}activatePoint(t){t.setAttribute("active","")}deactivatePoint(t){t.removeAttribute("active","")}_createNodeBox(){const t=document.createElement("div");t.classList.add(this._nodeClass);const e=document.createElement("div");e.classList.add(this._nodeBoxMainClass);const s=document.createElement("div");s.classList.add(this._nodeBoxTopClass);const i=document.createElement("div");i.classList.add(this._nodeBoxBottomClass);const n=document.createElement("div");n.classList.add(this._nodeBoxLeftClass),n.setAttribute("bus","left");const o=document.createElement("div");return o.classList.add(this._nodeBoxRightClass),o.setAttribute("bus","right"),t.append(e,n,o,s,i),{node:t,nodeMain:e}}_getSelectedFields(t){return{uid:t[this._key.uid],title:t[this._key.title],relations:t[this._key.relations]}}_setType(t,e){console.assert(e[this._key.type],"A node must always have a TYPE."),t.setAttribute("type",e[this._key.type])}_setUID(t,e){e[this._key.uid]&&t.setAttribute("uid",e[this._key.uid])}_setMID(t,e){e[this._key.mid]&&t.setAttribute("mid",e[this._key.mid])}_createField(t,e){switch(t){case this._key.title:return this._createTitleElement(e);case this._key.uid:return this._createUIDElement(e);case this._key.relations:break;default:return this._createCustomField(t,e)}}_createCustomField(t,e){const s=this._createFieldElement(),i=this._createFieldTitle(t),n=this._createFieldValue(e);return s.append(i,n),s}_createTitleElement(t){const e=document.createElement("div");return e.classList.add(this._nodeTitleClass),t&&(e.innerHTML=t),e}_createUIDElement(t){const e=document.createElement("code");return e.classList.add(this._nodeUIDClass),t&&(e.innerHTML=t),e}_createFieldElement(){const t=document.createElement("div");return t.classList.add(this._fieldClass),t}_createFieldTitle(t){const e=document.createElement("div");return e.classList.add(this._fieldTitleClass),t&&(e.innerHTML=t+":"),e}_createFieldValue(t){const e=document.createElement("div");return e.classList.add(this._fieldValueClass),t&&(e.innerHTML=t),e}}class y{constructor(t){this.svg,this.svgDefs,this._g,this._xmlns="http://www.w3.org/2000/svg",this._defaultStrokeColor="green",this._activeStrokeColor="orange",this._careStrokeColor="red",this._defaultStrokeWidth=2,this._defaultStrokeOpacity=1,this._arrowHeadID="arrowHead",this._arrowHeadW=4,this._arrowHeadH=5,this._maxDistance=500,this._minCurvature=50,this._maxCurvature=200,this._content=t,this._init()}_init(){this._createSvg(this._content),this._g=this._createGroup(),this.svg.append(this._g)}show(t){t.style.opacity=1}hide(t){t.style.opacity=0}activate(t){t.path.style.opacity=1,t.path.setAttributeNS(null,"stroke",this._activeStrokeColor)}deactivate(t){t.path.style.opacity=0,t.path.setAttributeNS(null,"stroke",this._defaultStrokeColor)}render(t){const e=t.side==="left"?1:-1,s=t.sourcePoint.offsetLeft,i=t.sourcePoint.offsetTop,n=t.targetPoint.offsetLeft+e*3*this._arrowHeadH,o=t.targetPoint.offsetTop,a=this._connectingPath(s,i,n,o);return a.setAttribute("relation",t.index),this._g.append(a),this.hide(a),a}_createSvg(){this.svg=document.createElementNS(this._xmlns,"svg"),this._content.append(this.svg),this.svg.setAttributeNS(null,"style","position: absolute; top: 0; left: 0; z-index: 10; user-select: none; pointer-events: none;"),this.updateSVG(),this.svgDefs=document.createElementNS(this._xmlns,"defs"),this.svg.append(this.svgDefs),this.svgDefs.innerHTML+=this._arrowHead()}updateSVG(){const t=this._content.offsetHeight,e=this._content.offsetWidth;this.svg.setAttributeNS(null,"viewBox",`0,0,${e},${t}`),this.svg.setAttributeNS(null,"width",e),this.svg.setAttributeNS(null,"height",t)}_createGroup({stroke:t=this._defaultStrokeColor,strokeWidth:e=this._defaultStrokeWidth*2,strokeOpacity:s=this._defaultStrokeOpacity}={}){const i=document.createElementNS(this._xmlns,"g");return i.setAttributeNS(null,"fill","none"),i.setAttributeNS(null,"stroke",t),i.setAttributeNS(null,"stroke-width",e),i.setAttributeNS(null,"stroke-opacity",s),i.setAttributeNS(null,"stroke-linecap","round"),i}_connectingPath(t=100,e=100,s=300,i=300,{stroke:n=this._defaultStrokeColor,strokeWidth:o=this._defaultStrokeWidth,strokeOpacity:a=this._defaultStrokeOpacity,arrowHeadSafeguard:r=this._arrowHeadH}={}){const h=Math.max(this._minCurvature,Math.min(this._maxCurvature,Math.abs(t-s)/this._maxDistance*(this._maxCurvature-this._minCurvature)+this._minCurvature)),d=document.createElementNS(this._xmlns,"path");d.setAttributeNS(null,"fill","none"),d.setAttributeNS(null,"stroke",n),d.setAttributeNS(null,"stroke-width",o),d.setAttributeNS(null,"stroke-opacity",a),d.setAttributeNS(null,"marker-end",`url(#${this._arrowHeadID})`);const u=-(t>s)||1;let l=t+u*h,b=s-u*h,m="";return r?m=`M ${t} ${e} L ${t+u*r} ${e} C ${l+u*r} ${e} ${b-u*r} ${i} ${s-u*r} ${i} L ${s} ${i}`:m=`M ${t} ${e} C ${l} ${e}, ${b} ${i}, ${s} ${i}`,d.setAttributeNS(null,"d",m),d}_arrowHead(t=this._arrowHeadW,e=this._arrowHeadH){return`
      <marker
        id='${this._arrowHeadID}'
        orient="auto-start-reverse"
        markerWidth='${e}'
        markerHeight='${t}'
        refX='0.1'
        refY='${t/2}'
      >
      <path d='M0,0 V${t} L${e},${t*.5} Z' fill='context-stroke' />
      </marker>`}pathC(t=100,e=100,s=300,i=300,{stroke:n=this._defaultStrokeColor,strokeWidth:o=this._defaultStrokeWidth,strokeOpacity:a=this._defaultStrokeOpacity,curvature:r=40}={}){const h=document.createElementNS(this._xmlns,"path");h.setAttributeNS(null,"fill","none"),h.setAttributeNS(null,"stroke",n),h.setAttributeNS(null,"stroke-width",o),h.setAttributeNS(null,"stroke-opacity",a),h.setAttributeNS(null,"marker-end",`url(#${this._arrowHeadID})`);const d=-(t>s)||1;let u=t+d*r,l=s-d*r;return h.setAttributeNS(null,"d",`M ${t} ${e} C ${u} ${e}, ${l} ${i}, ${s} ${i}`),h}pathQ({stroke:t="green",strokeWidth:e=this._defaultStrokeWidth,strokeOpacity:s=this._defaultStrokeOpacity}={}){const i=document.createElementNS(this._xmlns,"path");return i.setAttributeNS(null,"fill","none"),i.setAttributeNS(null,"stroke",t),i.setAttributeNS(null,"stroke-width",e),i.setAttributeNS(null,"stroke-opacity",s),i.setAttributeNS(null,"d","M20,230 Q40,205 50,230 T90,230"),i}line(t,e,s,i,{stroke:n="red",strokeWidth:o=this._defaultStrokeWidth,strokeOpacity:a=this._defaultStrokeOpacity}={}){const r=document.createElementNS(this._xmlns,"line");return r.setAttributeNS(null,"fill","none"),r.setAttributeNS(null,"stroke",n),r.setAttributeNS(null,"stroke-width",o),r.setAttributeNS(null,"stroke-opacity",a),r.setAttributeNS(null,"x1",t),r.setAttributeNS(null,"y1",e),r.setAttributeNS(null,"x2",s),r.setAttributeNS(null,"y2",i),r}}class S{constructor({content:t,graph:e,canvas:s,key:i={documents:"DOCUMENTS",nodes:"NODES",mid:"MID",title:"TITLE",uid:"UID",relations:"RELATIONS",value:"VALUE",type:"TYPE",role:"ROLE"}}){g(this,"_overNodeEvent",t=>{const e=t.currentTarget.getAttribute("uid");this._graph.getNodeRelation(e).forEach(s=>{s.path&&this._connector.show(s.path)})});g(this,"_outNodeEvent",t=>{const e=t.currentTarget.getAttribute("uid");this._graph.getNodeRelation(e).forEach(s=>{this._activeRelation.has(s.index)&&console.log(this._activeRelation.has(s.index)),s.path&&!this._activeRelation.has(s.index)&&this._connector.hide(s.path)})});this._jsonKey={documents:i.documents,nodes:i.nodes,title:i.title,uid:i.uid,mid:i.mid,relations:i.relations,value:i.value,type:i.type,role:i.role},this._content=t,this._graph=e,this._canvas=s,this._nest=new v,this._node=new x,this._connector=new y(this._content),this._activePath=new Set,this._activeRelation=new Set}process(){this._graph.getDocument().forEach((t,e)=>{const s=this._nest.create(t.title);this._content.append(s),this._graph.updateDocument(e,{nest:s})}),this._graph.getNode().forEach((t,e)=>{const s=this._node.create(t),i=this._nest.create(s);this._graph.getParentNest(t).append(i),this._graph.updateNode(e,{node:s,nest:i})}),Object.entries(this._graph.getRelationType("Parent")).forEach(([t,e])=>{const s=this._graph.getNodeElementByUID(e.sourceUID),i=this._graph.getNodeElementByUID(e.targetUID),n=i.offsetLeft<s.offsetLeft?"left":"right",o=this._node.createRelationPoint(s,i,n,"source",t),a=this._node.createRelationPoint(i,s,this._oppositeSide(n),"target",t);this._graph.updateRelation(t,{sourcePoint:o,targetPoint:a,side:n}),this._graph.addRelationPoint(e)}),Object.entries(this._graph.getRelationType("Parent")).forEach(([t,e])=>{const s=this._connector.render(e);this._graph.updateRelation(e.index,{path:s})}),this._connector.updateSVG(),this._addRelationEventListeners()}_addRelationEventListeners(){Object.entries(this._graph.getRelationNode()).forEach(([t,e])=>{const s=this._graph.getNodeElementByUID(t);s.addEventListener("mouseover",this._overNodeEvent,!1),s.addEventListener("mouseout",this._outNodeEvent,!1)}),Object.entries(this._graph.getRelationType("Parent")).forEach(([t,e])=>{e.sourcePoint.addEventListener("mouseover",()=>this._overPointEvent(e),!1),e.sourcePoint.addEventListener("mouseout",()=>this._outPointEvent(e),!1),e.sourcePoint.addEventListener("click",s=>this._clickPointEvent(s,e.targetPoint),!1),e.targetPoint.addEventListener("mouseover",()=>this._overPointEvent(e),!1),e.targetPoint.addEventListener("mouseout",()=>this._outPointEvent(e),!1),e.targetPoint.addEventListener("click",s=>this._clickPointEvent(s,e.sourcePoint),!1)})}_overPointEvent(t){}_outPointEvent(t){}_clickPointEvent(t,e){const s=Number(e.getAttribute("relation"));t.altKey?this._activeRelation.has(s)?this._hideActiveRelation(this._graph.getRelation(s)):this._showActiveRelation(this._graph.getRelation(s)):(this._activeRelation.has(s)||this._showActiveRelation(this._graph.getRelation(s)),this._canvas.move(e.offsetLeft,e.offsetTop))}_showActiveRelation(t){this._connector.activate(t),this._node.activatePoint(t.sourcePoint),this._node.activatePoint(t.targetPoint),this._activeRelation.add(t.index)}_hideActiveRelation(t){this._connector.deactivate(t),this._node.deactivatePoint(t.sourcePoint),this._node.deactivatePoint(t.targetPoint),this._activeRelation.delete(t.index)}_oppositeSide(t){switch(t){case"left":return"right";case"right":return"left";case"top":return"bottom";case"bottom":return"top"}}}class ${constructor(t,e={documents:"DOCUMENTS",nodes:"NODES",mid:"MID",title:"TITLE",uid:"UID",relations:"RELATIONS",value:"VALUE",type:"TYPE",role:"ROLE"}){this.json=t,this.data={document:{index:[]},node:{index:[],uid:{},mid:{}},relation:{index:[],type:{},role:{},source:{},target:{},node:{}}},this._jsonKey={documents:e.documents,nodes:e.nodes,title:e.title,uid:e.uid,mid:e.mid,relations:e.relations,value:e.value,type:e.type,role:e.role}}create(){this._preprocess(this.json),this.updateNode(443,{title:"QWERTY"})}_preprocess(t){t[this._jsonKey.documents].forEach((e,s)=>{this._addDocument({index:s,uid:e[this._jsonKey.uid],title:e[this._jsonKey.title],data:e}),this._preprocessNodes(e,s)})}_preprocessNodes(t,e,s){t[this._jsonKey.nodes]&&t[this._jsonKey.nodes].length>0&&t[this._jsonKey.nodes].forEach(i=>{this._preprocessNode(i,e,s)})}_preprocessNode(t,e,s){const i=this._addNode({type:t[this._jsonKey.type],uid:t[this._jsonKey.uid],mid:t[this._jsonKey.mid],title:t[this._jsonKey.title],data:t,parentDocumentIndex:e,parentNodeIndex:s});this._preprocessNodeRelation(t),this._preprocessNodes(t,e,i)}_preprocessNodeRelation(t){t[this._jsonKey.relations]&&t[this._jsonKey.relations].length>0&&t[this._jsonKey.relations].forEach((e,s)=>this._addRelation({type:e[this._jsonKey.type],role:e[this._jsonKey.role],targetUID:e[this._jsonKey.value],sourceUID:t[this._jsonKey.uid],sourceData:t,data:e}))}_addDocument({index:t,uid:e,title:s,data:i=null}){const n=this.data.document.index.length,o={index:t??n,uid:e,title:s,data:i};this.data.document.index.push(o)}updateDocument(t,{uid:e,title:s,nest:i,data:n=null}){const o=this.data.document.index[t];e&&(o.uid=e),s&&(o.title=s),n&&(o.data=n),i&&(o.nest=i)}_addNode({index:t,type:e,uid:s,mid:i,title:n,data:o=null,parentDocumentIndex:a,parentNodeIndex:r}){const h=this.data.node.index.length,d={index:t??h,type:e,uid:s,mid:i,title:n,parentDocumentIndex:a,parentNodeIndex:r,data:o};return this.data.node.index.push(d),s&&(this.data.node.uid[s]=d),i&&(this.data.node.mid[i]=d),d.index}updateNode(t,{uid:e,mid:s,title:i,data:n=null,parentDocumentIndex:o,parentNodeIndex:a,node:r,nest:h}){const d=this.data.node.index[t];e&&(d.uid=e),s&&(d.mid=s),i&&(d.title=i),n&&(d.data=n),o&&(d.parentDocumentIndex=o),a&&(d.parentNodeIndex=a),r&&(d.node=r),h&&(d.nest=h)}_addRelationPoint(t,{sourcePoint:e,targetPoint:s,side:i}){this.data.relation.point}_addRelation({index:t,type:e,role:s,data:i=null,sourceData:n=null,sourceUID:o,targetUID:a}){const r=this.data.relation.index.length,h={index:t??r,type:e,role:s,data:i,sourceData:n,sourceUID:o,targetUID:a};this.data.relation.index.push(h),console.assert(o,"Relation must have sourceUID"),this.data.relation.source[o]=this.data.relation.source[o]??[],this.data.relation.source[o].push(h),console.assert(a,"Relation must have targetUID"),this.data.relation.target[a]=this.data.relation.target[a]??[],this.data.relation.target[a].push(h),e&&(this.data.relation.type[e]=this.data.relation.type[e]??{},this.data.relation.type[e][r]=h),s&&(this.data.relation.role[s]=this.data.relation.role[s]??{},this.data.relation.role[s][r]=h)}addRelationPoint(t){this.data.relation.node[t.sourceUID]=this.data.relation.node[t.sourceUID]??{},this.data.relation.node[t.targetUID]=this.data.relation.node[t.targetUID]??{},this.data.relation.node[t.sourceUID][t.targetUID]=t,this.data.relation.node[t.targetUID][t.sourceUID]=t}updateRelation(t,{type:e,role:s,data:i=null,sourceData:n=null,sourceUID:o,targetUID:a,sourcePoint:r,targetPoint:h,side:d,path:u}){const l=this.data.relation.index[t];e&&(l.type=e),s&&(l.role=s),i&&(l.data=i),n&&(l.sourceData=n),o&&(l.sourceUID=o),a&&(l.targetUID=a),r&&(l.sourcePoint=r),h&&(l.targetPoint=h),d&&(l.side=d),u&&(l.path=u)}getDocument(t){if(t===void 0)return this.data.document.index;const e=Number(t);if(Number.isInteger(e)&&e>=0)return this.data.document.index[t]}getParentNest(t){if(t.parentNodeIndex!==void 0)return this.getNode()[t.parentNodeIndex].nest;if(t.parentDocumentIndex!==void 0)return this.getDocument()[t.parentDocumentIndex].nest;console.error(index,t,"node has not parent node or document?")}getNode(t){if(t===void 0)return this.data.node.index;const e=Number(t);if(Number.isInteger(e)&&e>=0)return this.data.node.index[t]}getNodeElementByUID(t){return this.getNodeUID(t).node}getNodeUID(t,e){return t===void 0?this.data.node.uid:(console.assert(typeof t=="string","uid mast be a string"),e===void 0?this.data.node.uid[t]:(console.assert(typeof t=="string","uid mast be a string"),this.data.node.uid[t]))}getNodeMID(t){return t===void 0?this.data.node.mid:this.data.node.mid[t]}getRelation(t){if(t===void 0)return this.data.relation.index;const e=Number(t);if(Number.isInteger(e)&&e>=0)return this.data.relation.index[t]}getRelationType(t,e){if(t===void 0)return this.data.relation.type;{if(console.assert(typeof t=="string","type mast be a string"),e===void 0)return this.data.relation.type[t];const s=Number(e);if(Number.isInteger(s)&&s>=0)return this.data.relation.type[t][e]}}getRelationRole(t,e){if(t===void 0)return this.data.relation.role;{if(console.assert(typeof t=="string","role mast be a string"),e===void 0)return this.data.relation.role[t];const s=Number(e);if(Number.isInteger(s)&&s>=0)return this.data.relation.role[t][e]}}getRelationSource(t){return t===void 0?this.data.relation.source:(console.assert(typeof t=="string","uid mast be a string"),this.data.relation.source[t])}getRelationTarget(t){return t===void 0?this.data.relation.target:(console.assert(typeof t=="string","uid mast be a string"),this.data.relation.target[t])}getRelationNode(t){return t===void 0?this.data.relation.node:(console.assert(typeof t=="string","uid mast be a string"),this.data.relation.node[t])}getNodeRelation(t){if(t===void 0||typeof t!="string"){console.assert(typeof t=="string","uid mast be a string");return}else{const e=this.getRelationSource(t),s=this.getRelationTarget(t);return[...e||[],...s||[]]}}_updateTree(t,e,s){switch(t){case"document":let i=e[this._jsonKey.title];if(this.data.document[i]){let o;do o=i+Math.floor(Math.random()*1e3);while(this.data.document[o]);i=o}this.data.document[i]={element:s};break;case"node":this.data.node.add({element:s,data:e}),e[this._jsonKey.mid]?this.data.nodeHasMID[e[this._jsonKey.mid]]={element:s,data:e}:this.data.noMID.push(s),e[this._jsonKey.uid]?this.data.nodeHasUID[e[this._jsonKey.uid]]={element:s,data:e}:this.data.noUID.push(s);const n=e[this._jsonKey.uid];e[this._jsonKey.relations]&&e[this._jsonKey.relations].length&&e[this._jsonKey.relations].forEach(o=>{const a=o[this._jsonKey.type];this.data.relation[a]||(this.data.relation[a]={source:{},target:{}});const r=o[this._jsonKey.value];(!this.data.relation[a].source[n]||!this.data.relation[a].source[n].length)&&(this.data.relation[a].source[n]=[]),this.data.relation[a].source[n].push({uid:r,type:a,role:o[this._jsonKey.role]}),(!this.data.relation[a].target[r]||!this.data.relation[a].target[r].length)&&(this.data.relation[a].target[r]=[]),this.data.relation[a].target[r].push({uid:n,type:a,role:o[this._jsonKey.role]})});break}}}class w{constructor(){this.content=document.createElement("div")}render(t){document.addEventListener("DOMContentLoaded",()=>{document.querySelector("#app").append(this.content);const e=new f({content:this.content});e.addPreloader(),e.addEventListener("scaleChange",this.onScaleChange),this.fetchData(t,s=>{const i=new $(s);i.create(),console.warn("%cApp: graph.data","font-weight:bold;color:violet",i.data),console.warn("%cApp: relation","font-weight:bold;color:black",i.data.relation),new S({content:this.content,graph:i,canvas:e}).process(),e.removePreloader()})})}async fetchData(t,e){const i=await(await fetch(t)).json();return console.warn("%cApp: fetch response:","font-weight:bold;color:green",i),e&&e(i),setTimeout(()=>{},3e3),i}onScaleChange(t){}}return w});
