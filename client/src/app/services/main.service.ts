import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable()
export class MainService {
  private endpoint = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  test() {
    return this.http.get(`${this.endpoint}/test`);
  }
}
