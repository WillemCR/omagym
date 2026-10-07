# frozen_string_literal: false
require 'minitest/autorun'
require_relative 'main'
class CalendarTest < Minitest::Test
  def setup
    @calendar=BookingCalendar.new
  end
  def book(id,room,first,last)
    @calendar.book(id:id,room:room,start_at:first,end_at:last)
  end
  def test_sorted_adjacent_bookings
    assert_same(true,book('later','A',20,30)); assert_same(true,book('early','A',10,20))
    assert_equal([{id:'early',room:'A',start_at:10,end_at:20},{id:'later',room:'A',start_at:20,end_at:30}],@calendar.bookings('A'))
  end
  def test_overlap_is_atomic
    book('a','A',10,20); book('c','A',30,40)
    [[9,11],[11,19],[19,21],[9,21],[10,20],[29,31],[35,45],[15,35]].each { |first,last| assert_raises(ArgumentError) { book('bad','A',first,last) } }
    assert_equal(['a','c'],@calendar.bookings('A').map { |x| x[:id] }); assert book('b','B',10,20)
  end
  def test_duplicate_and_invalid_inputs
    book('a','A',1,2); assert_raises(ArgumentError) { book('a','B',3,4) }
    [['','A',1,2],[' b','A',1,2],['b',' ',1,2],['b','A',2,2],['b','A',3,2],['b','A',1.5,2],['b','A','1',2]].each { |args| assert_raises(ArgumentError) { book(*args) } }
    assert_equal(1,@calendar.bookings('A').size)
  end
  def test_cancellation_and_isolation
    book('a','A',1,2); assert_same(true,@calendar.cancel('a')); assert_same(false,@calendar.cancel('a')); assert_equal([],@calendar.bookings('A')); assert_equal([],BookingCalendar.new.bookings('A')); assert_equal([],@calendar.bookings('unknown'))
    book('b','A',1,2); book('e','A',3,4); book('c','B',1,2); assert_same(true,@calendar.cancel('b')); assert_equal([{id:'e',room:'A',start_at:3,end_at:4}],@calendar.bookings('A')); assert_same(true,@calendar.cancel('e')); assert_same(false,@calendar.cancel('missing'))
    assert_equal([],@calendar.bookings('A')); assert_equal(['c'],@calendar.bookings('B').map { |x| x[:id] })
    other=BookingCalendar.new; assert_equal(['c'],@calendar.bookings('B').map { |x| x[:id] }); assert_equal([],other.bookings('B'))
    assert_same(true,other.book(id:'c',room:'B',start_at:1,end_at:2)); assert_equal(['c'],@calendar.bookings('B').map { |x| x[:id] }); assert book('d','B',5,6)
    assert_equal(['c'],other.bookings('B').map { |x| x[:id] }); assert_same(true,other.cancel('c')); assert_equal(['c','d'],@calendar.bookings('B').map { |x| x[:id] })
  end
  def test_defensive_copies
    id='a';room='A';book(id,room,1,2);id.replace('changed');room.replace('changed');result=@calendar.bookings('A');result[0][:id].replace('outside');result[0][:room].replace('outside');result[0][:start_at]=99
    assert_equal([{id:'a',room:'A',start_at:1,end_at:2}],@calendar.bookings('A'))
  end
end
