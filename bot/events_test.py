import unittest
from unittest.mock import patch, MagicMock
from bot.cogs import events
from bot import iracing

class TestEmbeds(unittest.TestCase):
    @patch('discord.Embed')
    @patch('arrow.get')
    def test_session_completed(self, mock_get, mock_embed):
        # Arrange
        mock_get.return_value.format.return_value = '2022-01-01 00:00'
        mock_embed.return_value = MagicMock()
        data = {
            'start_time': '2022-01-01T00:00:00Z',
            'end_time': '2022-01-01T01:00:00Z',
            'starting_position': 1,
            'finish_position': 2,
            'event_best_lap_time': 60000,
            'series_name': 'Test Series',
            'subsession_id': '123',
            'display_name': 'Test User',
            'track': {'track_name': 'Test Track', 'config_name': 'Test Config'},
            'winner_name': 'Winner User',
            'event_strength_of_field': 100,
            'laps_complete': 10,
            'laps_led': 5,
            'incidents': 0
        }

        # Act
        events_instance = events.Events(MagicMock())
        events.embeds().session_completed(data)

        # Assert
        mock_get.assert_any_call(data['start_time'])
        mock_get.assert_any_call(data['end_time'])
        mock_embed.assert_called_once()
        mock_embed.return_value.add_field.assert_any_call(name="Series", value=data['series_name'], inline=False)
        # Add more assertions for each field added to the embed

if __name__ == '__main__':
    unittest.main()