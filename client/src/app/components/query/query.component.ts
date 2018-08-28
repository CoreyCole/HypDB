import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { CsvJson, QueryRes, MainService } from '../../services/main.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'hyp-query',
  template: `
  <div class="container">
    <div class="input">
      <h1>Select CSV</h1>
      <mat-form-field>
        <mat-select placeholder="input file">
          <mat-option *ngFor="let file of files" [value]="file" (blur)="getCsvJson(file)">
            {{ file.substring(0, file.length - 5) }}
          </mat-option>
        </mat-select>
      </mat-form-field>
    </div>
    <div class="input">
      <h1>Data Subset</h1>
      <mat-form-field class="where">
        <input matInput type="text" placeholder="Subset of data" [(ngModel)]="where" autocomplete="off">
      </mat-form-field>
    </div>
  </div>
  <mat-spinner *ngIf="loading" color="accent"></mat-spinner>
  <hyp-pick-params [csvJson]="csvJson | async" [where]="where" (naiveAte)="naiveAte.emit($event)" (results)="queryResults($event)" (clear)="clearCalled()"></hyp-pick-params>
  `,
  styleUrls: ['./query.component.scss']
})
export class QueryComponent implements OnInit {
  @Input() files: string[];
  @Output() naiveAte = new EventEmitter<any[]>();
  @Output() results = new EventEmitter<QueryRes>();
  @Output() clear = new EventEmitter<void>();
  csvJson: Observable<CsvJson>;
  where: string;
  loading = false;

  constructor(private main: MainService) { }

  ngOnInit() {
  }

  getCsvJson(filename: string) {
    this.loading = true;
    this.csvJson = this.main.downloadCsvJson(filename);
    this.csvJson.subscribe(() => this.loading = false);
    this.clear.emit();
  }

  clearCalled() {
    this.clear.emit();
  }

  queryResults(data: QueryRes) {
    this.results.emit(data);
  }

}
