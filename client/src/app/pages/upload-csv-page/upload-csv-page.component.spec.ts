import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadCsvPageComponent } from './upload-csv-page.component';

describe('UploadCsvPageComponent', () => {
  let component: UploadCsvPageComponent;
  let fixture: ComponentFixture<UploadCsvPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UploadCsvPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UploadCsvPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
