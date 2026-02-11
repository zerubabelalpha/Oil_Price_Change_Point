import React from 'react';
import { Info } from 'lucide-react';

const EventList = ({ events, onEventClick, selectedEvent }) => {
    return (
        <div className="events-panel">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <Info size={18} color="#38bdf8" />
                <h3 style={{ margin: 0 }}>Historical Events</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {events.map((event, idx) => (
                    <div
                        key={idx}
                        className="event-item"
                        style={selectedEvent === event ? { backgroundColor: '#334155', borderLeft: '4px solid #38bdf8' } : {}}
                        onClick={() => onEventClick(event)}
                    >
                        <div className="event-date">{event.Start_Date}</div>
                        <div className="event-name">{event.Event_Name}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span className="event-category">{event.Category}</span>
                        </div>
                        {selectedEvent === event && (
                            <p style={{ fontSize: '0.8125rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                                {event.Description}
                            </p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EventList;
