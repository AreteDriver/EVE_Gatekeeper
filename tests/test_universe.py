def test_system_lookup():
    from evemap.universe import Universe
    u = Universe()
    assert u.get_system("Jita") is not None
