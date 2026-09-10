import test from 'node:test';
import assert from 'node:assert/strict';
import { summarizeExpenses } from './main.js';
test('empty_records', () => { assert.deepEqual(summarizeExpenses([]), []); });
test('group_and_sort', () => { assert.deepEqual(summarizeExpenses([{category:' food ',cents:80},{category:'travel',cents:300},{category:'food',cents:220},{category:'books',cents:10}]), [{category:'food',cents:300,count:2},{category:'travel',cents:300,count:1},{category:'books',cents:10,count:1}]); });
test('safe_keys_and_case', () => { assert.deepEqual(summarizeExpenses([{category:'__proto__',cents:0},{category:'a',cents:0},{category:'A',cents:0}]), [{category:'A',cents:0,count:1},{category:'__proto__',cents:0,count:1},{category:'a',cents:0,count:1}]); });
test('immutable_input', () => { const records=Object.freeze([Object.freeze({category:' x ',cents:4,extra:true}),Object.freeze({category:'x',cents:1})]); assert.deepEqual(summarizeExpenses(records),[{category:'x',cents:5,count:2}]); assert.equal(records[0].category,' x '); });
test('invalid_records', () => { for(const bad of [null,{},'x',[null],[{}],[{category:' ',cents:1}],[{category:2,cents:1}],...[NaN,Infinity,-1,1.5,'2',Number.MAX_SAFE_INTEGER+1].map(cents=>[{category:'x',cents}])]) assert.throws(()=>summarizeExpenses(bad),TypeError); });
test('total_overflow', () => { assert.throws(()=>summarizeExpenses([{category:'x',cents:Number.MAX_SAFE_INTEGER},{category:'x',cents:1}]),RangeError); assert.deepEqual(summarizeExpenses([{category:'x',cents:Number.MAX_SAFE_INTEGER}]),[{category:'x',cents:Number.MAX_SAFE_INTEGER,count:1}]); });
