import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FineGrainedComponent } from './fine-grained.component';

describe('FineGrainedComponent', () => {
  let component: FineGrainedComponent;
  let fixture: ComponentFixture<FineGrainedComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FineGrainedComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FineGrainedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
