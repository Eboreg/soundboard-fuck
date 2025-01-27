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


def get_test_sounds():
    root = Path("/home/klaatu/Soundboard/")
    data = [
        ("Ah, Music", 81, root / "Ah, Music.flac"),
        ("AI final human invention", 84, root / "AI final human invention.wav"),
        ("AI, the Singularity", 78, root / "AI, the Singularity.wav"),
        ("Algometrics", 10, root / "Algometrics.wav"),
        ("ba dum tss", 116, root / "ba dum tss.flac"),
        ("Baby Rock lång", 206, root / "Baby Rock lång.flac"),
        ("Baby Rock", 80, root / "Baby Rock.flac"),
        ("Badsalt 1", 61, root / "Badsalt 1.flac"),
        ("Badsalt 2", 172, root / "Badsalt 2.flac"),
        ("Barnes & Barnes YEAH!", 176, root / "Barnes & Barnes YEAH!.wav"),
        ("Ben's Radio", 155, root / "Ben's Radio.flac"),
        ("Bisarra hörnan", 141, root / "Bisarra hörnan.flac"),
        ("blunderfield 1", 163, root / "blunderfield 1.mp3"),
        ("blunderfield 3", 52, root / "blunderfield 3.mp3"),
        ("blygdläppar kort", 146, root / "blygdläppar kort.flac"),
        ("Bobbo Viking", 72, root / "Bobbo Viking.flac"),
        ("Bobby Callender John", 75, root / "Bobby Callender John.wav"),
        ("Boing Boom Tschak", 34, root / "Boing Boom Tschak.flac"),
        ("Brita Borg-skratt", 186, root / "Brita Borg-skratt.flac"),
        ("Communicatioooooon", 190, root / "Communicatioooooon.flac"),
        ("Communism is good", 44, root / "Communism is good.flac"),
        ("Cool Britannia", 119, root / "Cool Britannia.flac"),
        ("Cousin Mosquito COUSIN COUSIN", 28, root / "Cousin Mosquito COUSIN COUSIN.flac"),
        ("Cousin Mosquito Mooosquiiii", 62, root / "Cousin Mosquito Mooosquiiii.flac"),
        ("Cousin Mosquito sting of death", 108, root / "Cousin Mosquito sting of death.flac"),
        ("Cousin Mosquito use DDT", 68, root / "Cousin Mosquito use DDT.flac"),
        ("Cow-punching gay boy", 24, root / "Cow-punching gay boy.flac"),
        ("Cum gutters", 165, root / "Cum gutters.wav"),
        ("Den ariske mannens skor", 158, root / "Den ariske mannens skor.flac"),
        ("Det Ballar Ur", 6, root / "Det Ballar Ur.flac"),
        ("Det svaga röda vinet", 82, root / "Det svaga röda vinet.mp3"),
        ("Donovan starfish", 5, root / "Donovan starfish.flac"),
        ("Drupa", 90, root / "Drupa.wav"),
        ("eating the dogs", 193, root / "eating the dogs.wav"),
        ("Ed Sanders", 60, root / "Ed Sanders.flac"),
        ("egolE", 131, root / "egolE.flac"),
        ("Egyptian Lover", 139, root / "Egyptian Lover.wav"),
        ("Eloge", 192, root / "Eloge.flac"),
        ("Eternally grateful Dizzy", 12, root / "Eternally grateful Dizzy.flac"),
        ("Fast and bulbuous kort", 204, root / "Fast and bulbuous kort.wav"),
        ("Fast and bulbuous lång", 73, root / "Fast and bulbuous lång.wav"),
        ("Fffllpll & määzzö & gyckslllp", 25, root / "Fffllpll & määzzö & gyckslllp.wav"),
        ("Flim Flam Flum", 191, root / "Flim Flam Flum.flac"),
        ("Foreshadowing long", 152, root / "Foreshadowing long.wav"),
        ("Foreshadowing short", 162, root / "Foreshadowing short.wav"),
        ("Fowley teenage woman", 150, root / "Fowley teenage woman.flac"),
        ("Fred Titmus", 169, root / "Fred Titmus.flac"),
        ("Fuck, suck and fight", 145, root / "Fuck, suck and fight.flac"),
        ("Fünke Excuuuse me", 86, root / "Fünke Excuuuse me.flac"),
        ("Fünke HUZZAH", 41, root / "Fünke HUZZAH.flac"),
        ("Gayniggers 1", 118, root / "Gayniggers 1.flac"),
        ("Gayniggers female creatures 2", 38, root / "Gayniggers female creatures 2.flac"),
        ("Gayniggers female creatures kort", 125, root / "Gayniggers female creatures kort.flac"),
        ("Gayniggers gay universe kort", 200, root / "Gayniggers gay universe kort.flac"),
        ("Gayway to heaven kort", 207, root / "Gayway to heaven kort.flac"),
        ("Gayway to heaven", 182, root / "Gayway to heaven.flac"),
        ("Gediget arbete", 69, root / "Gediget arbete.flac"),
        ("Gunesh-fanfar", 31, root / "Gunesh-fanfar.flac"),
        ("Hallon bästa kiosken", 93, root / "Hallon bästa kiosken.flac"),
        ("Hallon du är ju inte klok", 95, root / "Hallon du är ju inte klok.flac"),
        ("Hallon Hallon!!", 144, root / "Hallon Hallon!!.flac"),
        ("Hallon hur fan är det med dig karl", 198, root / "Hallon hur fan är det med dig karl.flac"),
        ("Hard driving rock", 180, root / "Hard driving rock.flac"),
        ("Helikoptern Kräks", 54, root / "Helikoptern Kräks.wav"),
        ("hemläxa", 76, root / "hemläxa.wav"),
        ("hemläxa(1)", 164, root / "hemläxa(1).wav"),
        ("High vibration entity", 208, root / "High vibration entity.flac"),
        ("Hocus Pocus", 181, root / "Hocus Pocus.flac"),
        ("Hory shiet", 35, root / "Hory shiet.flac"),
        ("Humpp use my body", 51, root / "Humpp use my body.flac"),
        ("HUUH!! kort", 40, root / "HUUH!! kort.flac"),
        ("I am cum kort", 63, root / "I am cum kort.flac"),
        ("I am cum", 142, root / "I am cum.flac"),
        ("I'm a criminal", 134, root / "I'm a criminal.wav"),
        ("I'm gay 1", 97, root / "I'm gay 1.flac"),
        ("I'm gay 2", 137, root / "I'm gay 2.flac"),
        ("impatient with stupidity", 39, root / "impatient with stupidity.wav"),
        ("In a Glass House", 21, root / "In a Glass House.flac"),
        ("Interrupt this programme", 120, root / "Interrupt this programme.flac"),
        ("It's A Challenge!", 168, root / "It's A Challenge!.flac"),
        ("jaaazzz", 55, root / "jaaazzz.flac"),
        ("Jag samlar på lår", 0, root / "Jag samlar på lår.flac"),
        ("Jajja Lasse Lönndahl!", 171, root / "Jajja Lasse Lönndahl!.flac"),
        ("Jeremy Fragrance kicking fucking", 100, root / "Jeremy Fragrance kicking fucking.flac"),
        ("Jeremy Fragrance stimulated penis", 33, root / "Jeremy Fragrance stimulated penis.flac"),
        ("Jim Gillette POWER kort", 205, root / "Jim Gillette POWER kort.wav"),
        ("Jim Gillette POWER", 127, root / "Jim Gillette POWER.flac"),
        ("Jim Gillette what a rush", 48, root / "Jim Gillette what a rush.flac"),
        ("Jimmy Carl Black", 189, root / "Jimmy Carl Black.flac"),
        ("Jod-Kaliklora", 159, root / "Jod-Kaliklora.flac"),
        ("Kambodja är befriat", 14, root / "Kambodja är befriat.wav"),
        ("Kanye Hitler", 138, root / "Kanye Hitler.wav"),
        ("Katrineholmstant", 160, root / "Katrineholmstant.wav"),
        ("KF - Kate (SILENCE)", 92, root / "KF - Kate (SILENCE).flac"),
        ("KF - Lizzie (MRS M)", 117, root / "KF - Lizzie (MRS M).flac"),
        ("KF - Lizzie", 196, root / "KF - Lizzie.flac"),
        ("Kicking it oldschool", 166, root / "Kicking it oldschool.flac"),
        ("Killer Condom", 126, root / "Killer Condom.flac"),
        ("Kleenex", 177, root / "Kleenex.flac"),
        ("Ku Klux Klan", 16, root / "Ku Klux Klan.wav"),
        ("La di da poofter", 123, root / "La di da poofter.flac"),
        ("La Polka du colonel", 32, root / "La Polka du colonel.flac"),
        ("Leary Spin slowly", 106, root / "Leary Spin slowly.flac"),
        ("Leary You are light", 151, root / "Leary You are light.flac"),
        ("Lou Reed drugs", 49, root / "Lou Reed drugs.flac"),
        ("Lou Reed transvestite", 102, root / "Lou Reed transvestite.flac"),
        ("Love har gjort en låt", 20, root / "Love har gjort en låt.flac"),
        ("Lucia Pamela", 107, root / "Lucia Pamela.flac"),
        ("Lugosi Pull the string", 74, root / "Lugosi Pull the string.flac"),
        ("Lyssnat på chiptune", 11, root / "Lyssnat på chiptune.mp3"),
        ("Lyssnat på Frej", 184, root / "Lyssnat på Frej.flac"),
        ("Lyssnat på koral", 13, root / "Lyssnat på koral.mp3"),
        ("Lyssnat på Monkey Island", 140, root / "Lyssnat på Monkey Island.mp3"),
        ("Lyssnat på OG", 149, root / "Lyssnat på OG.flac"),
        ("Lyssnat på rapping v2", 133, root / "Lyssnat på rapping v2.flac"),
        ("Lyssnat på rapping", 3, root / "Lyssnat på rapping.mp3"),
        ("Lyssnat på stråk", 188, root / "Lyssnat på stråk.mp3"),
        ("Lyssnat_dramatiskLOVE", 173, root / "Lyssnat_dramatiskLOVE.mp3"),
        ("Magma-vinjett", 202, root / "Magma-vinjett.flac"),
        ("mao tse tungs tanke", 99, root / "mao tse tungs tanke.flac"),
        ("Marinetti 1", 194, root / "Marinetti 1.flac"),
        ("Marinetti 2", 110, root / "Marinetti 2.flac"),
        ("Mashup", 135, root / "Mashup.wav"),
        ("mashup2", 53, root / "mashup2.wav"),
        ("moa_003 nähej", 70, root / "moa_003 nähej.flac"),
        ("moa_003", 1, root / "moa_003.flac"),
        ("Morbid Angel Mahummuhu Gal-Gal", 71, root / "Morbid Angel Mahummuhu Gal-Gal.flac"),
        ("Motherfuckeeeer", 56, root / "Motherfuckeeeer.flac"),
        ("musikens makt kort", 85, root / "musikens makt kort.flac"),
        ("musikens makt", 153, root / "musikens makt.flac"),
        ("My god is Lucifer 1", 195, root / "My god is Lucifer 1.flac"),
        ("My god is Lucifer 2", 65, root / "My god is Lucifer 2.flac"),
        ("My meditations 1", 156, root / "My meditations 1.flac"),
        ("My meditations 2", 37, root / "My meditations 2.flac"),
        ("My meditations 3", 203, root / "My meditations 3.flac"),
        ("My poisoned semen", 2, root / "My poisoned semen.flac"),
        ("MYSTERY TRACK boing boing", 59, root / "MYSTERY TRACK boing boing.flac"),
        ("MYSTERY TRACK fanfar", 8, root / "MYSTERY TRACK fanfar.flac"),
        ("MYSTERY TRACK", 26, root / "MYSTERY TRACK.flac"),
        ("Niggers come in every colour kort", 4, root / "Niggers come in every colour kort.flac"),
        ("Nikuta o jee", 103, root / "Nikuta o jee.flac"),
        ("Oh God Oh Man", 87, root / "Oh God Oh Man.flac"),
        ("Oh no", 183, root / "Oh no.wav"),
        ("Ohio Plus-Y0dLhWl6cD8", 104, root / "Ohio Plus-Y0dLhWl6cD8.flac"),
        ("Ory's Creole Trombone", 17, root / "Ory's Creole Trombone.flac"),
        ("Pachuco Cadaver", 111, root / "Pachuco Cadaver.wav"),
        ("Palme pajaskonster", 148, root / "Palme pajaskonster.flac"),
        ("Patreon", 91, root / "Patreon.flac"),
        ("PJ Proby I am the passenger", 124, root / "PJ Proby I am the passenger.flac"),
        ("PJ Proby I love you", 45, root / "PJ Proby I love you.flac"),
        ("PJ Proby I say la", 129, root / "PJ Proby I say la.flac"),
        ("PurpleDave", 201, root / "PurpleDave.flac"),
        ("Ray Charles Wooo", 154, root / "Ray Charles Wooo.flac"),
        ("Robert är en kommunist", 42, root / "Robert är en kommunist.flac"),
        ("Robert spelar banjo", 57, root / "Robert spelar banjo.flac"),
        ("robert topp last fm-låtar år efter år", 101, root / "robert topp last fm-låtar år efter år.flac"),
        ("Rock'n'roll-valsen(1)", 174, root / "Rock'n'roll-valsen(1).flac"),
        ("Roland-JV-2080-Orchestra-Hit-C3", 130, root / "Roland-JV-2080-Orchestra-Hit-C3.wav"),
        ("rorsman", 199, root / "rorsman.flac"),
        ("Sitter och RUNKAR", 167, root / "Sitter och RUNKAR.wav"),
        (
            "Skiva sammanfattad som en spänstig och fräsch mix",
            19,
            root / "Skiva sammanfattad som en spänstig och fräsch mix.flac",
        ),
        ("Slog smutsen in i mig", 27, root / "Slog smutsen in i mig.wav"),
        ("Spännande", 122, root / "Spännande.wav"),
        ("spermjacking", 30, root / "spermjacking.wav"),
        ("Spike Milligan Q5 Piano Tune", 128, root / "Spike Milligan Q5 Piano Tune.flac"),
        ("Splittringen var bra och nödvändig", 29, root / "Splittringen var bra och nödvändig.wav"),
        ("suck his own dick", 114, root / "suck his own dick.wav"),
        ("Suomi Finland Perkele", 89, root / "Suomi Finland Perkele.flac"),
        ("Surprise 1", 88, root / "Surprise 1.wav"),
        ("Surprise 2", 50, root / "Surprise 2.wav"),
        ("Tack för det Televerket", 175, root / "Tack för det Televerket.flac"),
        ("The metal kings kort", 15, root / "The metal kings kort.flac"),
        ("There you go", 67, root / "There you go.wav"),
        ("Things ghastly", 83, root / "Things ghastly.flac"),
        ("Things horrible mess", 143, root / "Things horrible mess.flac"),
        ("Things wicked piss", 147, root / "Things wicked piss.flac"),
        ("Too much of a musician", 161, root / "Too much of a musician.flac"),
        ("Tou", 22, root / "Tou.wav"),
        ("Touching others and ourselves", 23, root / "Touching others and ourselves.wav"),
        ("Troll 2", 170, root / "Troll 2.flac"),
        ("Trouble with pigs and ponies", 187, root / "Trouble with pigs and ponies.wav"),
        ("Uff, unka", 98, root / "Uff, unka.wav"),
        ("Uggla 1977", 47, root / "Uggla 1977.flac"),
        ("Uh! Ain't it funky now!", 36, root / "Uh! Ain't it funky now!.flac"),
        ("Uh! Disco!", 112, root / "Uh! Disco!.flac"),
        ("Uh! Sorry!", 105, root / "Uh! Sorry!.flac"),
        ("Uh!", 109, root / "Uh!.flac"),
        ("Ulf Ekman 1 halleluja", 136, root / "Ulf Ekman 1 halleluja.wav"),
        ("Ulf Ekman 2", 79, root / "Ulf Ekman 2.wav"),
        ("Ulf Ekman 3", 178, root / "Ulf Ekman 3.wav"),
        ("Vafan är meningen", 121, root / "Vafan är meningen.wav"),
        ("Vrålande getto av vindruvor", 43, root / "Vrålande getto av vindruvor.wav"),
        ("White Lines Base 1", 64, root / "White Lines Base 1.flac"),
        ("White Lines Base 2", 66, root / "White Lines Base 2.flac"),
        ("White motherfuckers 1", 96, root / "White motherfuckers 1.flac"),
        ("White motherfuckers 2", 9, root / "White motherfuckers 2.flac"),
        ("winamp", 132, root / "winamp.flac"),
        ("Yezda Urfa", 113, root / "Yezda Urfa.flac"),
        ("Yngwie fury", 46, root / "Yngwie fury.flac"),
        ("Yngwie more is more", 18, root / "Yngwie more is more.flac"),
        ("You're under arrest!", 58, root / "You're under arrest!.flac"),
        ("Zacharias å vad kåt jag är", 77, root / "Zacharias å vad kåt jag är.flac"),
        ("Zacharias fingret i skitan", 7, root / "Zacharias fingret i skitan.flac"),
        ("Zacharias hela jävla pungen i mun", 94, root / "Zacharias hela jävla pungen i mun.flac"),
        ("Zacharias spanska spöt", 185, root / "Zacharias spanska spöt.flac"),
        ("Zacharias underbara lustar", 179, root / "Zacharias underbara lustar.flac"),
        ("Zappa-jingel", 157, root / "Zappa-jingel.flac"),
    ]

    return [
        Sound(name=t[0], id=t[1], path=t[2], category_id=0, colors=ColorScheme.BLUE)
        for t in data
    ]
