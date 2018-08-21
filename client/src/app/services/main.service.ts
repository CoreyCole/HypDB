import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

export interface CsvJson {
  delimeter?: string;
  linebreak?: string;
  fields?: string[];
  filename?: string;
  uploadDate?: string;
}

export interface HypDBDto {
  outcome: string;
  filename: string;
  where: string;
  groupingAttributes: string[];
}

export interface QueryRes {
  ate: any[][];
  graph: GraphData;
}

export interface GraphData {
  correlation: {
    dashed: boolean;
    treatment: string[];
    outcome: string[];
  },
  links: GraphLink[];
  nodes: GraphNode[];
}

export interface GraphLink {
  source: string;
  target: string;
}

export interface GraphNode {
  id: string;
  label: string;
}

@Injectable()
export class MainService {
  private endpoint = 'http://localhost:5000';
  files: Observable<string[]> = of([]);
  private queryResCache = new Map<string, QueryRes>();

  constructor(private http: HttpClient) { }

  test() {
    return this.http.get(`${this.endpoint}/test`);
  }

  postJSON(csvJSON) {
    console.log(`${this.endpoint}/api/bias`);
    return this.http.post(`${this.endpoint}/api/bias`, { json: csvJSON });
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

  queryNaiveAte(dto: HypDBDto): Observable<any[]> {
    return this.http.post(`${this.endpoint}/api/bias/ate`, { ...dto })
      .pipe(
        catchError(err => of(err))
      );
  }

  queryHypDb(dto: HypDBDto): Observable<QueryRes> {
    console.log(dto);
    const key = this.getKey(dto);
    if (this.queryResCache.has(key)) {
      const result = this.queryResCache.get(key);
      console.log('cached result=', result);
      return of(result);
    } else {
      return this.http.post(`${this.endpoint}/api/bias`, { ...dto })
        .pipe(
          catchError(err => throwError(err)),
          tap((res: QueryRes) => {
            this.queryResCache.set(key, res);
          })
        );
    }
  }

  refreshFiles() {
    this.files = this.getCsvJsonUploadList();
  }

  private getKey(dto: HypDBDto): string {
    return dto.filename + dto.outcome + dto.groupingAttributes.toString() + dto.where;
  }
}
