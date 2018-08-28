import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import * as SqlWhereParser from 'sql-where-parser';

import { CsvJson, HypDBDto, QueryRes, MainService } from '../../../services/main.service';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'hyp-pick-params',
  template: `
  <div *ngIf="csvJson">
    <span class="error">{{ error }}</span>
    <div class="spacer"></div>
    <div class="inputs">
      <pre>       SELECT avg(</pre>
      <div class="auto-complete outcome">
        <mat-form-field>
          <input matInput placeholder="" [matAutocomplete]="tdAuto" [(ngModel)]="currentOutcome"
            (ngModelChange)="outcomeAttrs = filterAttributes(currentOutcome)" name="outcome">
        </mat-form-field>
        <mat-autocomplete #tdAuto="matAutocomplete">
          <mat-option *ngFor="let attr of outcomeAttrs" [value]="attr">
            <span>{{ attr }}</span>
          </mat-option>
        </mat-autocomplete>    
      </div>  
      <pre>)</pre>
      <br />
      <pre>       FROM {{ csvJson.filename.substring(0, csvJson.filename.length - 4) }}</pre>
      <pre *ngIf="where">WHERE {{ where }}</pre>
      <br />
      <pre>       GROUP BY</pre>
      <div class="auto-complete treatment">
        <mat-form-field>
          <input matInput placeholder="" [matAutocomplete]="tdAuto2" [(ngModel)]="currentTreatment"
            (ngModelChange)="treatAttrs = filterAttributes(currentTreatment)" name="treatment">
        </mat-form-field>
        <mat-autocomplete #tdAuto2="matAutocomplete">
          <mat-option *ngFor="let attr of treatAttrs" [value]="attr">
            <span>{{ attr }}</span>
          </mat-option>
        </mat-autocomplete>    
      </div>
    </div>
    <div class="spacer"></div>
    <div *ngIf="!loading" class="buttons">
      <button mat-raised-button (click)="clearQuery()">CLEAR</button>
      <button mat-raised-button color="accent" (click)="query()">QUERY</button>
    </div>
    <div class="loading">
      <mat-spinner *ngIf="loading" color="accent"></mat-spinner>
      <span *ngIf="loading" class="message">The query is being diagnosed for bias . . .</span>
    </div>
  </div>
  `,
  styleUrls: ['./pick-params.component.scss']
})
export class PickParamsComponent implements OnChanges {
  @Input() csvJson: CsvJson;
  @Input() where: string;
  @Output() results = new EventEmitter<QueryRes>();
  @Output() naiveAte = new EventEmitter<any[]>();
  @Output() clear = new EventEmitter<void>();
  error: string;
  whereParser = new SqlWhereParser();
  loading = false;
  currentTreatment: string = null;
  currentOutcome: string = null;
  treatAttrs: string[];
  outcomeAttrs: string[];

  constructor(private main: MainService) { }

  ngOnChanges() {
    // this.clearQuery();
    if (this.csvJson) {
      this.treatAttrs = this.csvJson.fields;
      this.outcomeAttrs = this.csvJson.fields;
    }
  }

  filterAttributes(val: string) {
    return val ? this._filter(this.csvJson.fields, val) : this.csvJson.fields;
  }

  private _filter(attributes: string[], val: string) {
    const filterValue = val.toLowerCase();
    return attributes.filter(attribute => attribute.toLowerCase().startsWith(filterValue));
  }

  clearQuery() {
    this.currentOutcome = null;
    this.currentTreatment = null;
    this.treatAttrs = [];
    this.outcomeAttrs = [];
    this.where = '';
    this.error = null;
    this.clear.emit();
  }

  query() {
    if (!this.currentOutcome) {
      this.error = 'no outcome selected!';
    } else if (!this.currentTreatment) {
      this.error = 'no treatment selected!';
    } else {
      this.error = null;
      this.loading = true;
      const parsedWhere = this.whereParser.parse(this.where);
      const dto: HypDBDto = {
        outcome: this.currentOutcome,
        // groupingAttributes: [this.treatment, ...this.groupingAttributes],
        groupingAttributes: [this.currentTreatment],
        filename: this.csvJson.filename,
        where: parsedWhere,
        whereString: this.where || 'undefined'
      };
      this.main.queryNaiveAte(dto)
        .subscribe(data => {
          console.log(data);
          this.naiveAte.emit(data);
        });
      this.main.queryHypDb(dto)
        .pipe(
          catchError((err) => {
            this.loading = false;
            this.results.emit(null);
            return throwError(err);
          })
        )
        .subscribe(data => {
          console.log(data);
          this.results.emit(data);
          this.loading = false;
        });
    }
  }

}
