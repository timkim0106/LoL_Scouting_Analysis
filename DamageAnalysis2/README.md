# League of Legends Analytics Framework

Python framework for League of Legends damage calculations and player analysis.

## Features

### Core Analytics
- Champion damage analysis across different builds and scenarios
- Professional player tracking and performance monitoring
- Statistical analysis with Monte Carlo simulations and confidence intervals
- Data visualization for build comparisons

### Architecture
- Type safety with Pydantic data validation
- Environment-based configuration
- Structured logging with file rotation
- Error handling and API rate limiting

### Analytics
- Build optimization across armor/MR ranges
- Gold efficiency analysis
- Damage calculations with special item mechanics (Eclipse, Muramana)
- Statistical confidence intervals

## Installation

### Prerequisites
- Python 3.8+
- Riot Games API Key

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd LoLAccountAnalysis/DamageAnalysis2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.template .env
# Edit .env with your Riot API key
```

4. Install the package:
```bash
pip install -e .
```

## Configuration

Create a `.env` file with your settings:

```env
RIOT_API_KEY=RGAPI-your-api-key-here
RIOT_REGION=americas
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///lol_analytics.db
```

## Quick Start

### Basic Champion Analysis

```python
from lol_analytics.core import ChampionAnalyzer
from lol_analytics.models.item import ITEM_SETS

# Initialize analyzer
analyzer = ChampionAnalyzer()

# Compare Jayce builds
builds = {
    "Eclipse + Muramana + Serylda": ITEM_SETS["Eclipse_Muramana_Serylda"],
    "Eclipse + Muramana + LDR": ITEM_SETS["Eclipse_Muramana_LDR"]
}

# Analyze builds
analysis = analyzer.analyze_item_builds(
    champion_name="Jayce",
    combo=['Q2', 'W2', 'E2', 'R1', 'E1Q1', 'W1A'],
    builds=builds,
    level=13
)

print(f"Best build: {analysis['best_build']}")
```

### Professional Player Tracking

```python
from lol_analytics.core import PlayerTracker

# Initialize tracker
tracker = PlayerTracker()

# Add professional players
players = [
    {"game_name": "C9 Berserker", "tag_line": "NA1", "team": "C9", "role": "ADC"},
    {"game_name": "TL CoreJJ", "tag_line": "1123", "team": "TL", "role": "SUPPORT"}
]

results = tracker.batch_add_players(players)

# Analyze performance
for puuid in tracker.players:
    analysis = tracker.analyze_player_performance(puuid)
    if analysis:
        print(f"{analysis['player']}: {analysis['overall_win_rate']:.1f}% WR")
```

### Advanced Damage Analysis

```python
# Run armor range analysis
armor_analysis = analyzer.run_armor_analysis(
    champion_name="Jayce",
    combo=['Q2', 'W2', 'E2', 'R1', 'E1Q1'],
    builds=builds,
    armor_range=(30, 200),
    save_plot=True
)

# Monte Carlo simulation
from lol_analytics.analytics import DamageCalculator

calculator = DamageCalculator()
simulation = calculator.monte_carlo_damage_simulation(
    champion=analyzer.get_champion("Jayce"),
    combo=['E1Q1'],
    items=ITEM_SETS["Eclipse_Muramana_Serylda"],
    iterations=10000
)

print(f"Expected damage: {simulation['mean']:.1f} ± {simulation['std']:.1f}")
```

## Examples

Run the comprehensive example:

```bash
python example_analysis.py
```

This demonstrates:
- Champion build comparisons
- Armor range analysis  
- Multi-champion comparisons
- Professional player tracking
- Statistical analysis

## Architecture

```
lol_analytics/
├── core/                   # Main analysis engines
│   ├── champion_analyzer.py
│   └── player_tracker.py
├── models/                 # Data models
│   ├── base.py
│   ├── champion.py
│   ├── item.py
│   └── player.py
├── analytics/              # Advanced analytics
│   ├── damage_calculator.py
│   └── statistical_analyzer.py
├── utils/                  # Utilities
│   ├── api_client.py
│   └── logger.py
├── config/                 # Configuration
│   └── settings.py
└── data/                   # Data files
    └── champion_data.json
```

## Champion Analysis Features

### Damage Calculations
- Ability damage modeling with champion-specific mechanics
- Item effect calculations (Eclipse, Muramana, etc.)
- Armor/magic resistance penetration
- Special mechanics implementation

### Build Optimization
- Gold efficiency analysis
- Damage per gold calculations
- Crossover point analysis
- Statistical confidence intervals

### Visualization
- Damage vs armor curves
- Build comparison charts
- Differential analysis plots

## Player Tracking Features

### Data Collection
- Account monitoring and performance tracking
- Name change detection
- Match history analysis
- Performance metrics calculation

### Professional Teams
- LCS team rosters
- Role-based analysis
- Team performance summaries

### Analytics
- Win rate calculations
- Champion performance analysis
- Trend identification

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=lol_analytics
```

## License

MIT License - see LICENSE file for details.

---

**Note**: This project requires a valid Riot Games API key. Visit the [Riot Developer Portal](https://developer.riotgames.com/) to obtain one.