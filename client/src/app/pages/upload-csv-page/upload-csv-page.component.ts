import { Component, OnInit } from '@angular/core';
import { MainService } from '../../services/main.service';

@Component({
  selector: 'hyp-upload-csv-page',
  template: `
  <mat-toolbar color="primary">
    HypDB - Upload CSV
    <span class="flex-span"></span>
    <button mat-raised-button color="accent" routerLink="/home">HOME PAGE</button>
  </mat-toolbar>
  <div class="container">
    <h1>Press to upload a csv file to HypDB backend</h1>
    <hyp-csv-upload (uploadedFile)="refreshFiles()"></hyp-csv-upload>
  </div>
  `,
  styleUrls: ['./upload-csv-page.component.scss']
})
export class UploadCsvPageComponent implements OnInit {

  constructor(private main: MainService) { }

  ngOnInit() {
  }

  refreshFiles() {
    this.main.refreshFiles();
  }

}

