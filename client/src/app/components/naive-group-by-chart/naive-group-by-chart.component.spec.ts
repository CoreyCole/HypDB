import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NaiveGroupByChartComponent } from './naive-group-by-chart.component';

describe('NaiveGroupByChartComponent', () => {
  let component: NaiveGroupByChartComponent;
  let fixture: ComponentFixture<NaiveGroupByChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NaiveGroupByChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NaiveGroupByChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
