import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CsvJson {
  data: any[];
  errors: any[];
  meta: {
    delimeter?: string;
    linebreak?: string;
    fields?: string[];
    filename?: string;
    uploadDate?: string;
  }
}

export interface HypDBDto {
  outcome: string;
  filename: string;
  where: string;
  groupingAttribute: string;
}

@Injectable()
export class MainService {
  private endpoint = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  test() {
    return this.http.get(`${this.endpoint}/test`);
  }

  getCsvJsonUploadList(): Observable<string[]> {
    return this.http.get<string[]>(`${this.endpoint}/csv-json`);
  }

  uploadCsvJson(csvJson: CsvJson) {
    return this.http.post(`${this.endpoint}/csv-json/upload`, { json: csvJson });
  }

  downloadCsvJson(filename: string): Observable<CsvJson> {
    return this.http.get<CsvJson>(`${this.endpoint}/csv-json/download/${filename}`);
  }

  queryHypDb(dto: HypDBDto) {
    console.log(dto);
    return this.http.post(`${this.endpoint}/api/bias`, { ...dto });
  }
}
