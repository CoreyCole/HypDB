import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DagDemoComponent } from './dag-demo.component';

describe('DagDemoComponent', () => {
  let component: DagDemoComponent;
  let fixture: ComponentFixture<DagDemoComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DagDemoComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DagDemoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
