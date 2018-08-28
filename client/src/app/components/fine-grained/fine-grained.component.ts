import { Component, OnChanges, Input } from '@angular/core';

@Component({
  selector: 'hyp-fine-grained',
  template: `
  <div class="datatable">
    <mat-toolbar color="accent">
      <span>Fine Grained Attribute Data</span>
      <span class="flex-span"></span>
      <span class="select-span">
        <mat-select
          #currK
          [placeholder]="'k = 3'"
          [value]="3"
          (valueChange)="kSelected(currK.value)">
          <mat-option *ngFor="let row of fineGrained.attributes[currentCovariate].rows; index as i" [value]="i+1">
            k = {{ i+1 }}
          </mat-option>
        </mat-select>
      </span>
      <span class="flex-span"></span>
      <span class="select-span">
        <mat-select
          #selectedAttribute
          placeholder="attribute"
          [value]="currentCovariate"
          (valueChange)="attributeSelected(selectedAttribute.value)">
          <mat-option *ngFor="let attribute of covariates" [value]="attribute">
            {{ attribute }}
          </mat-option>
        </mat-select>
      </span>
    </mat-toolbar>
    <ngx-datatable
      class="material"
      [rows]="rows"
      [columns]="columns"
      [columnMode]="'force'"
      [headerHeight]="50"
      [footerHeight]="50"
      [rowHeight]="'auto'">
    </ngx-datatable>
  </div>
  `,
  styleUrls: ['./fine-grained.component.scss']
})
export class FineGrainedComponent implements OnChanges {
  @Input() fineGrained: {
    attributes: { string: { columns: string[], rows: any[] } },
    outcome: string[];
    treatment: string[];
  };
  covariates: string[];
  currentCovariate: string;
  columns: any[];
  rows: any[];
  maxK: number;
  currK: number;

  constructor() { }

  ngOnChanges() {
    if (this.fineGrained) {
      this.covariates = Object.keys(this.fineGrained.attributes);
      this.currentCovariate = this.covariates[0];
      this.columns = this.fineGrained.attributes[this.currentCovariate].columns.map(column => {
        return { name: column };
      });
      this.maxK = this.fineGrained.attributes[this.currentCovariate].rows.length;
      this.currK = 3;
      this.rows = this.fineGrained.attributes[this.currentCovariate].rows.slice(0, this.currK);
    }
  }

  kSelected(newK: number) {
    this.currK = newK;
    this.rows = this.fineGrained.attributes[this.currentCovariate].rows.slice(0, this.currK);
  }

  attributeSelected(attribute: string) {
    this.currentCovariate = attribute;
    this.columns = this.fineGrained.attributes[attribute].columns.map(column => {
      return { name: column };
    });
    this.rows = this.fineGrained.attributes[attribute].rows;
  }

}
