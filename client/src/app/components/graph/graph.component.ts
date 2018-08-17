import { Component, Input, OnChanges } from '@angular/core';
import * as shape from 'd3-shape';

import { GraphLink, GraphNode, GraphData } from '../../services/main.service';

@Component({
  selector: 'hyp-graph',
  template: `
  <span>{{error}}</span>
  <div class="ngx-graph-container">
    <ngx-graph *ngIf="graph"
      class="chart-container"
      [view]="view"
      [legend]="false"
      [links]="links"
      [nodes]="nodes"
      [scheme]="colorScheme"
      [curve]="curve"
      [enableZoom]="false"
      [draggingEnabled]="true"
      [panningEnabled]="false">

      <ng-template #defsTemplate let-link>
        <svg:marker id="arrow" viewBox="0 -5 10 10" refX="8" refY="0" markerWidth="8" markerHeight="8" orient="auto">
          <svg:path d="M0,-5L10,0L0,5" class="arrow-head" />
        </svg:marker>
      </ng-template>

      <ng-template #nodeTemplate let-node>
        <svg:g class="node"
          ngx-tooltip
          [tooltipPlacement]="'top'"
          [tooltipType]="'tooltip'"
          [tooltipTitle]="node.label">
          <svg:rect [attr.width]="node.width + 10" [attr.height]="node.height + 10" [attr.fill]="getColor(node)" fill-opacity="0.4" />
          <svg:text alignment-baseline="central" [attr.x]="10" [attr.y]="(node.height + 10)/ 2">{{node.label}}</svg:text>
        </svg:g>
      </ng-template>

      <ng-template #linkTemplate let-link>
        <svg:g class="edge">
          <svg:path *ngIf="directed(link)"
            class="line"
            [ngClass]="{'dashed': dashed(link), 'bold': bold(link)}"
            attr.id="{{link.source}}-to-{{link.target}}"
            stroke-width="2"
            marker-end="url(#arrow)" >
          </svg:path>
          <svg:path *ngIf="!directed(link)"
            class="line"
            [ngClass]="{'dashed': dashed(link), 'bold': bold(link)}"
            attr.id="{{link.source}}-to-{{link.target}}"
            stroke-width="2">
          </svg:path>
        </svg:g>
      </ng-template>

    </ngx-graph>
  </div>
  `,
  styleUrls: ['./graph.component.scss']
})
export class GraphComponent implements OnChanges {
  @Input() graph: GraphData;
  links: GraphLink[];
  nodes: GraphNode[];
  error: string;

  view: any[] = [900, 400];
  curve = shape.curveLinear; // or some other function from d3-shape
  colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
  };
  orientations: any[] = [
    {
      label: 'Left to Right',
      value: 'LR'
    },
    {
      label: 'Right to Left',
      value: 'RL'
    },
    {
      label: 'Top to Bottom',
      value: 'TB'
    },
    {
      label: 'Bottom to Top',
      value: 'BT'
    }
  ];
  constructor() { }

  ngOnChanges() {
    // if (this.graph && this.invalid(this.graph)) {
    //   this.links = [];
    //   this.nodes = [];
    //   this.error = 'outcome found to be parent of the treatment';
    // } else if (this.graph) {
    // this.links = this.graph.links;
    // this.nodes = this.graph.nodes;
    // }
    if (this.graph) {
      this.links = this.graph.links;
      this.nodes = this.graph.nodes;
      console.log('treatment', this.graph.correlation.treatment);
      console.log('outcome', this.graph.correlation.outcome[0]);
      console.log('dashed', this.graph.correlation.dashed);
    }
  }

  private invalid(graph: GraphData): boolean {
    const treatment = graph.correlation.treatment[0];
    const outcome = graph.correlation.outcome[0];
    for (const link of graph.links) {
      if (link.source === outcome && link.target === treatment) {
        // outcome cannot be the parent of the treatment
        return true;
      }
    }
  }

  getColor(node: GraphNode): string {
    const label = node.label;
    if (this.graph.correlation.treatment.indexOf(label) > -1) {
      return "rgb(199, 180, 44)";
    } else if (this.graph.correlation.outcome.indexOf(label) > -1) {
      return "rgb(90, 164, 84)";
    } else {
      return "rgb(170, 170, 170)";
    }
  }

  directed(link: GraphLink): boolean {
    const treatment = this.graph.correlation.treatment[0];
    const outcome = this.graph.correlation.outcome[0];
    if (link.source === outcome) {
      return false;
    } else if (link.target === outcome) {
      return true;
    } else if (link.source === treatment) {
      return false;
    } else if (link.target === treatment) {
      return true;
    }
    return false;
  }

  dashed(link: GraphLink): boolean {
    if (this.graph.correlation.treatment.indexOf(link.source) > -1  // source is a treatment
      && this.graph.correlation.outcome.indexOf(link.target) > -1   // target is outcome
      && this.graph.correlation.dashed) {
      return true
    }
    return false;
  }

  bold(link: GraphLink): boolean {
    if (this.graph.correlation.treatment.indexOf(link.source) > -1  // source is a treatment
      && this.graph.correlation.outcome.indexOf(link.target) > -1   // target is outcome
      && !this.graph.correlation.dashed) {
      return true
    }
    return false;
  }

}
