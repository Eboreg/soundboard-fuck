from dataclasses import dataclass, field
from pathlib import Path

from pydub import AudioSegment

from soundboard_fuck.ui.colors import ColorScheme
from soundboard_fuck.utils import str_to_floats


@dataclass
class Sound:
    name: str
    id: int
    path: Path
    category_id: int
    colors: ColorScheme
    duration_ms: int | None = None
    play_count: int = 0

    name_floats: tuple[float, float] = field(init=False)
    format: str = field(init=False)

    @property
    def duration_seconds(self) -> float | None:
        return self.duration_ms / 1000 if self.duration_ms is not None else None

    def __post_init__(self):
        self.name_floats = str_to_floats(self.name)
        self.format = self.path.suffix.strip(".").lower()

    def __hash__(self):
        return self.id

    def copy(
        self,
        name: str | None = None,
        path: Path | None = None,
        duration_ms: int | None = None,
        play_count: int | None = None,
        category_id: int | None = None,
        colors: ColorScheme | None = None,
    ):
        return Sound(
            name=name if name is not None else self.name,
            id=self.id,
            path=path if path is not None else self.path,
            duration_ms=duration_ms if duration_ms is not None else self.duration_ms,
            play_count=play_count if play_count is not None else self.play_count,
            category_id=category_id if category_id is not None else self.category_id,
            colors=colors if colors is not None else self.colors,
        )

    @classmethod
    def extract_duration_ms(cls, path: Path) -> int | None:
        segment: AudioSegment = AudioSegment.from_file(file=path, format=path.suffix.strip(".").lower())
        if isinstance(segment.duration_seconds, (float, int)):
            return int(segment.duration_seconds * 1000)
        return None


def get_test_sounds(category_id: int):
    root = Path("/home/klaatu/Soundboard/")
    data = [
        ("Ah, Music", root / "Ah, Music.flac"),
        ("AI final human invention", root / "AI final human invention.wav"),
        ("AI, the Singularity", root / "AI, the Singularity.wav"),
        ("Algometrics", root / "Algometrics.wav"),
        ("ba dum tss", root / "ba dum tss.flac"),
        ("Baby Rock lång", root / "Baby Rock lång.flac"),
        ("Baby Rock", root / "Baby Rock.flac"),
        ("Badsalt 1", root / "Badsalt 1.flac"),
        ("Badsalt 2", root / "Badsalt 2.flac"),
        ("Barnes & Barnes YEAH!", root / "Barnes & Barnes YEAH!.wav"),
        ("Ben's Radio", root / "Ben's Radio.flac"),
        ("Bisarra hörnan", root / "Bisarra hörnan.flac"),
        ("blunderfield 1", root / "blunderfield 1.mp3"),
        ("blunderfield 3", root / "blunderfield 3.mp3"),
        ("blygdläppar kort", root / "blygdläppar kort.flac"),
        ("Bobbo Viking", root / "Bobbo Viking.flac"),
        ("Bobby Callender John", root / "Bobby Callender John.wav"),
        ("Boing Boom Tschak", root / "Boing Boom Tschak.flac"),
        ("Brita Borg-skratt", root / "Brita Borg-skratt.flac"),
        ("Communicatioooooon", root / "Communicatioooooon.flac"),
        ("Communism is good", root / "Communism is good.flac"),
        ("Cool Britannia", root / "Cool Britannia.flac"),
        ("Cousin Mosquito COUSIN COUSIN", root / "Cousin Mosquito COUSIN COUSIN.flac"),
        ("Cousin Mosquito Mooosquiiii", root / "Cousin Mosquito Mooosquiiii.flac"),
        ("Cousin Mosquito sting of death", root / "Cousin Mosquito sting of death.flac"),
        ("Cousin Mosquito use DDT", root / "Cousin Mosquito use DDT.flac"),
        ("Cow-punching gay boy", root / "Cow-punching gay boy.flac"),
        ("Cum gutters", root / "Cum gutters.wav"),
        ("Den ariske mannens skor", root / "Den ariske mannens skor.flac"),
        ("Det Ballar Ur", root / "Det Ballar Ur.flac"),
        ("Det svaga röda vinet", root / "Det svaga röda vinet.mp3"),
        ("Donovan starfish", root / "Donovan starfish.flac"),
        ("Drupa", root / "Drupa.wav"),
        ("eating the dogs", root / "eating the dogs.wav"),
        ("Ed Sanders", root / "Ed Sanders.flac"),
        ("egolE", root / "egolE.flac"),
        ("Egyptian Lover", root / "Egyptian Lover.wav"),
        ("Eloge", root / "Eloge.flac"),
        ("Eternally grateful Dizzy", root / "Eternally grateful Dizzy.flac"),
        ("Fast and bulbuous kort", root / "Fast and bulbuous kort.wav"),
        ("Fast and bulbuous lång", root / "Fast and bulbuous lång.wav"),
        ("Fffllpll & määzzö & gyckslllp", root / "Fffllpll & määzzö & gyckslllp.wav"),
        ("Flim Flam Flum", root / "Flim Flam Flum.flac"),
        ("Foreshadowing long", root / "Foreshadowing long.wav"),
        ("Foreshadowing short", root / "Foreshadowing short.wav"),
        ("Fowley teenage woman", root / "Fowley teenage woman.flac"),
        ("Fred Titmus", root / "Fred Titmus.flac"),
        ("Fuck, suck and fight", root / "Fuck, suck and fight.flac"),
        ("Fünke Excuuuse me", root / "Fünke Excuuuse me.flac"),
        ("Fünke HUZZAH", root / "Fünke HUZZAH.flac"),
        ("Gayniggers 1", root / "Gayniggers 1.flac"),
        ("Gayniggers female creatures 2", root / "Gayniggers female creatures 2.flac"),
        ("Gayniggers female creatures kort", root / "Gayniggers female creatures kort.flac"),
        ("Gayniggers gay universe kort", root / "Gayniggers gay universe kort.flac"),
        ("Gayway to heaven kort", root / "Gayway to heaven kort.flac"),
        ("Gayway to heaven", root / "Gayway to heaven.flac"),
        ("Gediget arbete", root / "Gediget arbete.flac"),
        ("Gunesh-fanfar", root / "Gunesh-fanfar.flac"),
        ("Hallon bästa kiosken", root / "Hallon bästa kiosken.flac"),
        ("Hallon du är ju inte klok", root / "Hallon du är ju inte klok.flac"),
        ("Hallon Hallon!!", root / "Hallon Hallon!!.flac"),
        ("Hallon hur fan är det med dig karl", root / "Hallon hur fan är det med dig karl.flac"),
        ("Hard driving rock", root / "Hard driving rock.flac"),
        ("Helikoptern Kräks", root / "Helikoptern Kräks.wav"),
        ("hemläxa", root / "hemläxa.wav"),
        ("hemläxa(1)", root / "hemläxa(1).wav"),
        ("High vibration entity", root / "High vibration entity.flac"),
        ("Hocus Pocus", root / "Hocus Pocus.flac"),
        ("Hory shiet", root / "Hory shiet.flac"),
        ("Humpp use my body", root / "Humpp use my body.flac"),
        ("HUUH!! kort", root / "HUUH!! kort.flac"),
        ("I am cum kort", root / "I am cum kort.flac"),
        ("I am cum", root / "I am cum.flac"),
        ("I'm a criminal", root / "I'm a criminal.wav"),
        ("I'm gay 1", root / "I'm gay 1.flac"),
        ("I'm gay 2", root / "I'm gay 2.flac"),
        ("impatient with stupidity", root / "impatient with stupidity.wav"),
        ("In a Glass House", root / "In a Glass House.flac"),
        ("Interrupt this programme", root / "Interrupt this programme.flac"),
        ("It's A Challenge!", root / "It's A Challenge!.flac"),
        ("jaaazzz", root / "jaaazzz.flac"),
        ("Jag samlar på lår", root / "Jag samlar på lår.flac"),
        ("Jajja Lasse Lönndahl!", root / "Jajja Lasse Lönndahl!.flac"),
        ("Jeremy Fragrance kicking fucking", root / "Jeremy Fragrance kicking fucking.flac"),
        ("Jeremy Fragrance stimulated penis", root / "Jeremy Fragrance stimulated penis.flac"),
        ("Jim Gillette POWER kort", root / "Jim Gillette POWER kort.wav"),
        ("Jim Gillette POWER", root / "Jim Gillette POWER.flac"),
        ("Jim Gillette what a rush", root / "Jim Gillette what a rush.flac"),
        ("Jimmy Carl Black", root / "Jimmy Carl Black.flac"),
        ("Jod-Kaliklora", root / "Jod-Kaliklora.flac"),
        ("Kambodja är befriat", root / "Kambodja är befriat.wav"),
        ("Kanye Hitler", root / "Kanye Hitler.wav"),
        ("Katrineholmstant", root / "Katrineholmstant.wav"),
        ("KF - Kate (SILENCE)", root / "KF - Kate (SILENCE).flac"),
        ("KF - Lizzie (MRS M)", root / "KF - Lizzie (MRS M).flac"),
        ("KF - Lizzie", root / "KF - Lizzie.flac"),
        ("Kicking it oldschool", root / "Kicking it oldschool.flac"),
        ("Killer Condom", root / "Killer Condom.flac"),
        ("Kleenex", root / "Kleenex.flac"),
        ("Ku Klux Klan", root / "Ku Klux Klan.wav"),
        ("La di da poofter", root / "La di da poofter.flac"),
        ("La Polka du colonel", root / "La Polka du colonel.flac"),
        ("Leary Spin slowly", root / "Leary Spin slowly.flac"),
        ("Leary You are light", root / "Leary You are light.flac"),
        ("Lou Reed drugs", root / "Lou Reed drugs.flac"),
        ("Lou Reed transvestite", root / "Lou Reed transvestite.flac"),
        ("Love har gjort en låt", root / "Love har gjort en låt.flac"),
        ("Lucia Pamela", root / "Lucia Pamela.flac"),
        ("Lugosi Pull the string", root / "Lugosi Pull the string.flac"),
        ("Lyssnat på chiptune", root / "Lyssnat på chiptune.mp3"),
        ("Lyssnat på Frej", root / "Lyssnat på Frej.flac"),
        ("Lyssnat på koral", root / "Lyssnat på koral.mp3"),
        ("Lyssnat på Monkey Island", root / "Lyssnat på Monkey Island.mp3"),
        ("Lyssnat på OG", root / "Lyssnat på OG.flac"),
        ("Lyssnat på rapping v2", root / "Lyssnat på rapping v2.flac"),
        ("Lyssnat på rapping", root / "Lyssnat på rapping.mp3"),
        ("Lyssnat på stråk", root / "Lyssnat på stråk.mp3"),
        ("Lyssnat_dramatiskLOVE", root / "Lyssnat_dramatiskLOVE.mp3"),
        ("Magma-vinjett", root / "Magma-vinjett.flac"),
        ("mao tse tungs tanke", root / "mao tse tungs tanke.flac"),
        ("Marinetti 1", root / "Marinetti 1.flac"),
        ("Marinetti 2", root / "Marinetti 2.flac"),
        ("Mashup", root / "Mashup.wav"),
        ("mashup2", root / "mashup2.wav"),
        ("moa_003 nähej", root / "moa_003 nähej.flac"),
        ("moa_003", root / "moa_003.flac"),
        ("Morbid Angel Mahummuhu Gal-Gal", root / "Morbid Angel Mahummuhu Gal-Gal.flac"),
        ("Motherfuckeeeer", root / "Motherfuckeeeer.flac"),
        ("musikens makt kort", root / "musikens makt kort.flac"),
        ("musikens makt", root / "musikens makt.flac"),
        ("My god is Lucifer 1", root / "My god is Lucifer 1.flac"),
        ("My god is Lucifer 2", root / "My god is Lucifer 2.flac"),
        ("My meditations 1", root / "My meditations 1.flac"),
        ("My meditations 2", root / "My meditations 2.flac"),
        ("My meditations 3", root / "My meditations 3.flac"),
        ("My poisoned semen", root / "My poisoned semen.flac"),
        ("MYSTERY TRACK boing boing", root / "MYSTERY TRACK boing boing.flac"),
        ("MYSTERY TRACK fanfar", root / "MYSTERY TRACK fanfar.flac"),
        ("MYSTERY TRACK", root / "MYSTERY TRACK.flac"),
        ("Niggers come in every colour kort", root / "Niggers come in every colour kort.flac"),
        ("Nikuta o jee", root / "Nikuta o jee.flac"),
        ("Oh God Oh Man", root / "Oh God Oh Man.flac"),
        ("Oh no", root / "Oh no.wav"),
        ("Ohio Plus-Y0dLhWl6cD8", root / "Ohio Plus-Y0dLhWl6cD8.flac"),
        ("Ory's Creole Trombone", root / "Ory's Creole Trombone.flac"),
        ("Pachuco Cadaver", root / "Pachuco Cadaver.wav"),
        ("Palme pajaskonster", root / "Palme pajaskonster.flac"),
        ("Patreon", root / "Patreon.flac"),
        ("PJ Proby I am the passenger", root / "PJ Proby I am the passenger.flac"),
        ("PJ Proby I love you", root / "PJ Proby I love you.flac"),
        ("PJ Proby I say la", root / "PJ Proby I say la.flac"),
        ("PurpleDave", root / "PurpleDave.flac"),
        ("Ray Charles Wooo", root / "Ray Charles Wooo.flac"),
        ("Robert är en kommunist", root / "Robert är en kommunist.flac"),
        ("Robert spelar banjo", root / "Robert spelar banjo.flac"),
        ("robert topp last fm-låtar år efter år", root / "robert topp last fm-låtar år efter år.flac"),
        ("Rock'n'roll-valsen(1)", root / "Rock'n'roll-valsen(1).flac"),
        ("Roland-JV-2080-Orchestra-Hit-C3", root / "Roland-JV-2080-Orchestra-Hit-C3.wav"),
        ("rorsman", root / "rorsman.flac"),
        ("Sitter och RUNKAR", root / "Sitter och RUNKAR.wav"),
        (
            "Skiva sammanfattad som en spänstig och fräsch mix",
            root / "Skiva sammanfattad som en spänstig och fräsch mix.flac",
        ),
        ("Slog smutsen in i mig", root / "Slog smutsen in i mig.wav"),
        ("Spännande", root / "Spännande.wav"),
        ("spermjacking", root / "spermjacking.wav"),
        ("Spike Milligan Q5 Piano Tune", root / "Spike Milligan Q5 Piano Tune.flac"),
        ("Splittringen var bra och nödvändig", root / "Splittringen var bra och nödvändig.wav"),
        ("suck his own dick", root / "suck his own dick.wav"),
        ("Suomi Finland Perkele", root / "Suomi Finland Perkele.flac"),
        ("Surprise 1", root / "Surprise 1.wav"),
        ("Surprise 2", root / "Surprise 2.wav"),
        ("Tack för det Televerket", root / "Tack för det Televerket.flac"),
        ("The metal kings kort", root / "The metal kings kort.flac"),
        ("There you go", root / "There you go.wav"),
        ("Things ghastly", root / "Things ghastly.flac"),
        ("Things horrible mess", root / "Things horrible mess.flac"),
        ("Things wicked piss", root / "Things wicked piss.flac"),
        ("Too much of a musician", root / "Too much of a musician.flac"),
        ("Tou", root / "Tou.wav"),
        ("Touching others and ourselves", root / "Touching others and ourselves.wav"),
        ("Troll 2", root / "Troll 2.flac"),
        ("Trouble with pigs and ponies", root / "Trouble with pigs and ponies.wav"),
        ("Uff, unka", root / "Uff, unka.wav"),
        ("Uggla 1977", root / "Uggla 1977.flac"),
        ("Uh! Ain't it funky now!", root / "Uh! Ain't it funky now!.flac"),
        ("Uh! Disco!", root / "Uh! Disco!.flac"),
        ("Uh! Sorry!", root / "Uh! Sorry!.flac"),
        ("Uh!", root / "Uh!.flac"),
        ("Ulf Ekman 1 halleluja", root / "Ulf Ekman 1 halleluja.wav"),
        ("Ulf Ekman 2", root / "Ulf Ekman 2.wav"),
        ("Ulf Ekman 3", root / "Ulf Ekman 3.wav"),
        ("Vafan är meningen", root / "Vafan är meningen.wav"),
        ("Vrålande getto av vindruvor", root / "Vrålande getto av vindruvor.wav"),
        ("White Lines Base 1", root / "White Lines Base 1.flac"),
        ("White Lines Base 2", root / "White Lines Base 2.flac"),
        ("White motherfuckers 1", root / "White motherfuckers 1.flac"),
        ("White motherfuckers 2", root / "White motherfuckers 2.flac"),
        ("winamp", root / "winamp.flac"),
        ("Yezda Urfa", root / "Yezda Urfa.flac"),
        ("Yngwie fury", root / "Yngwie fury.flac"),
        ("Yngwie more is more", root / "Yngwie more is more.flac"),
        ("You're under arrest!", root / "You're under arrest!.flac"),
        ("Zacharias å vad kåt jag är", root / "Zacharias å vad kåt jag är.flac"),
        ("Zacharias fingret i skitan", root / "Zacharias fingret i skitan.flac"),
        ("Zacharias hela jävla pungen i mun", root / "Zacharias hela jävla pungen i mun.flac"),
        ("Zacharias spanska spöt", root / "Zacharias spanska spöt.flac"),
        ("Zacharias underbara lustar", root / "Zacharias underbara lustar.flac"),
        ("Zappa-jingel", root / "Zappa-jingel.flac"),
    ]

    return [
        Sound(name=t[0], id=i, path=t[1], category_id=category_id, colors=ColorScheme.BLUE)
        for i, t in enumerate(data)
    ]
