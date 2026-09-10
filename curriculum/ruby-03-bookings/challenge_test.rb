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
    assert book('later','A',20,30); assert book('early','A',10,20)
    assert_equal([{id:'early',room:'A',start_at:10,end_at:20},{id:'later',room:'A',start_at:20,end_at:30}],@calendar.bookings('A'))
  end
  def test_overlap_is_atomic
    book('a','A',10,20)
    [[9,11],[11,19],[19,21],[9,21],[10,20]].each { |first,last| assert_raises(ArgumentError) { book('bad','A',first,last) } }
    assert_equal(['a'],@calendar.bookings('A').map { |x| x[:id] }); assert book('b','B',10,20)
  end
  def test_duplicate_and_invalid_inputs
    book('a','A',1,2); assert_raises(ArgumentError) { book('a','B',3,4) }
    [['','A',1,2],[' b','A',1,2],['b',' ',1,2],['b','A',2,2],['b','A',3,2],['b','A',1.5,2],['b','A','1',2]].each { |args| assert_raises(ArgumentError) { book(*args) } }
    assert_equal(1,@calendar.bookings('A').size)
  end
  def test_cancellation_and_isolation
    book('a','A',1,2); assert @calendar.cancel('a'); refute @calendar.cancel('a'); assert_equal([],@calendar.bookings('A')); assert_equal([],BookingCalendar.new.bookings('A')); assert_equal([],@calendar.bookings('unknown'))
  end
  def test_defensive_copies
    id='a';room='A';book(id,room,1,2);id.replace('changed');room.replace('changed');result=@calendar.bookings('A');result[0][:id].replace('outside');result[0][:room].replace('outside');result[0][:start_at]=99
    assert_equal([{id:'a',room:'A',start_at:1,end_at:2}],@calendar.bookings('A'))
  end
end
