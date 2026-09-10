class BookingCalendar
  def book(id:, room:, start_at:, end_at:)
    raise NotImplementedError, 'Register a valid non-overlapping booking'
  end
  def cancel(_id)
    raise NotImplementedError, 'Cancel a booking'
  end
  def bookings(_room)
    raise NotImplementedError, 'List room bookings'
  end
end
