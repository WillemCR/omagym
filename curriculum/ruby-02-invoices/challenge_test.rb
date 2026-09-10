# frozen_string_literal: false
require 'minitest/autorun'
require 'stringio'
require_relative 'main'
class InvoiceTest < Minitest::Test
  def test_header_only
    assert_equal({}, invoice_totals(StringIO.new("customer,cents\n")))
  end
  def test_grouped_integer_totals
    assert_equal({'Ada'=>35,'Bob'=>0},invoice_totals(StringIO.new("customer,cents\n Ada ,0010\nAda,25\nBob,0\n")))
  end
  def test_quoted_names_and_large_amounts
    assert_equal({'Acme, Inc'=>10**25},invoice_totals(StringIO.new("customer,cents\n\"Acme, Inc\",#{10**25}\n")))
  end
  def test_invalid_csv_and_rows
    ['',"cents,customer\n", "customer,cents\nx\n", "customer,cents\nx,1,2\n", "customer,cents\n,3\n", "customer,cents\n\"broken,3\n", *['-1','+1','1.5',' 1','1e3',''].map { |n| "customer,cents\nx,#{n}\n" }].each do |text|
      assert_raises(ArgumentError) { invoice_totals(StringIO.new(text)) }
    end
  end
  def test_io_is_not_closed
    io=StringIO.new("customer,cents\nx,1\n"); invoice_totals(io); refute io.closed?
  end
  def test_read_error_propagates
    error=IOError.new('unavailable'); io=Object.new; io.define_singleton_method(:read) { |*| raise error }; io.define_singleton_method(:gets) { |*| raise error }
    assert_same(error,assert_raises(IOError) { invoice_totals(io) })
  end
end
