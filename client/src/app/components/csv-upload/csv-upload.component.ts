import { Component, OnInit } from '@angular/core';

import { Papa } from 'ngx-papaparse';
import { PapaParseResult } from '../../../../node_modules/ngx-papaparse/lib/interfaces/papa-parse-result';
import { MainService } from '../../services/main.service';

@Component({
  selector: 'hyp-csv-upload',
  template: `
    <span class="error">{{ error }}</span>
    <div class="upload" *ngIf="!currentResultJson && !loading">
      <button mat-raised-button color="accent" (click)="uploadCsv($event)">UPLOAD CSV</button>
      <input id="file-upload" mat-raised-button type="file" (change)="fileSelected($event.target.files)">
    </div>
    <div class="confirm" *ngIf="currentResultJson && !loading">
      <h2>Confirm Columns</h2>
      <button mat-raised-button color="accent" (click)="confirmUpload()">LOOKS GOOD</button>
      <mat-list>
        <mat-list-item *ngFor="let column of confirmColumns">
          <i class="material-icons" mat-list-icon>
            done
          </i> 
          <h4 mat-line>{{ column }}</h4>
        </mat-list-item>
      </mat-list>
    </div>
    <mat-spinner *ngIf="loading" color="accent"></mat-spinner>
  `,
  styleUrls: ['./csv-upload.component.scss']
})
export class CsvUploadComponent implements OnInit {
  error: string;
  currentResultJson: PapaParseResult;
  confirmColumns: string[];
  loading = false;

  constructor(
    private papa: Papa,
    private main: MainService 
  ) { }

  ngOnInit() {
  }

  uploadCsv() {
    document.getElementById('file-upload').click();
  }

  fileSelected(files: FileList) {
    if (files.length > 1) return this.error = 'can only upload 1 file at a time!';
    const file: File = files[0];
    this.papa.parse(file, {
      header: true,
      complete: parsedResult => this.handleParsedJson(parsedResult),
      error: () => this.error = 'csv error'
    });
  }

  handleParsedJson(resultJson: PapaParseResult) {
    if (resultJson.errors) console.dir(resultJson.errors)
    this.currentResultJson = resultJson;
    this.confirmColumns = Object.keys(resultJson.data[0]);
  }

  confirmUpload() {
    const uploadJson = { ...this.currentResultJson };
    uploadJson['columns'] = [ ...this.confirmColumns ];
    
    // reset component fields
    this.error = '';
    this.currentResultJson = null;
    this.confirmColumns = null;
    
    // upload the json to the backend
    this.loading = true;
    this.main.uploadCsvJson(uploadJson)
      .subscribe(response => {
        console.log(response)
        this.loading = false;
      });
  }

}
