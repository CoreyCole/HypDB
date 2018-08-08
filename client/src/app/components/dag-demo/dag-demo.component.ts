import { Component, OnInit } from '@angular/core';
import * as shape from 'd3-shape';

@Component({
  selector: 'hyp-dag-demo',
  template: `
  <div class="ngx-graph-container">
    <ngx-graph
      class="chart-container"
      [view]="view"
      [legend]="false"
      [links]="links"
      (legendLabelClick)="onLegendLabelClick($event)"
      [nodes]="nodes"
      [scheme]="colorScheme"
      [orientation]="orientation"
      [curve]="curve"
      (select)="select($event)"
      [enableZoom]="false"
      [draggingEnabled]="true"
      [panningEnabled]="false">

      <ng-template #defsTemplate>
        <svg:marker id="arrow" viewBox="0 -5 10 10" refX="8" refY="0" markerWidth="4" markerHeight="4" orient="auto">
          <svg:path d="M0,-5L10,0L0,5" class="arrow-head" />
        </svg:marker>
      </ng-template>

      <ng-template #nodeTemplate let-node>
        <svg:g class="node"
          ngx-tooltip
          [tooltipPlacement]="'top'"
          [tooltipType]="'tooltip'"
          [tooltipTitle]="node.label">
          <svg:rect [attr.width]="node.width" [attr.height]="node.height" [attr.fill]="node.options.color" />
          <svg:text alignment-baseline="central" [attr.x]="10" [attr.y]="node.height / 2">{{node.label}}</svg:text>
        </svg:g>
      </ng-template>

      <ng-template #linkTemplate let-link>
        <svg:g class="edge">
          <svg:path
            class="line"
            stroke-width="2"
            marker-end="url(#arrow)" >
          </svg:path>
        </svg:g>
      </ng-template>

    </ngx-graph>
  </div>
  `,
  styleUrls: ['./dag-demo.component.scss']
})
export class DagDemoComponent implements OnInit {

  select(event) {
    console.log(event);
  }

  onLegendLabelClick(event) {
    console.log(event);
  }

  onZoom(event) {
    console.log(event)
  }

  curve = shape.curveLinear; // or some other function from d3-shape
  colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
  };
  nodes = [
    {
      id: 'start',
      label: 'start'
    }, {
      id: '1',
      label: 'Query ThreatConnect',
    }, {
      id: '2',
      label: 'Query XForce',
    }, {
      id: '3',
      label: 'Format Results'
    }, {
      id: '4',
      label: 'Search Splunk'
    }, {
      id: '5',
      label: 'Block LDAP'
    }, {
      id: '6',
      label: 'Email Results'
    }
  ];
  links = [
    {
      source: 'start',
      target: '1',
      label: 'links to'
    }, {
      source: 'start',
      target: '2'
    }, {
      source: '1',
      target: '3',
      label: 'related to'
    }, {
      source: '2',
      target: '4'
    }, {
      source: '2',
      target: '6'
    }, {
      source: '3',
      target: '5'
    }
  ];

  constructor() { }

  ngOnInit() {
  }

}
