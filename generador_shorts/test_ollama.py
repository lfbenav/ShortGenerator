from ollama import AsyncClient
import asyncio
texto = """
I (36M) have been married to my wife (34F) for five years and we have a 3 year old son together. My wife finished med school and residency program and she has been a neurology specialist for 4 years. I have a management job that pays well but my wife gets paid about 30% more than me. Despite the pay gap, almost all our son's expenses are covered by me and the bills are split evenly.

Recently my wife came up to me and talked about how she feels like she spent all her adult life working on her career and has always been stressed by the work load she had and now she feels like she should get the fruits of her labor, therefore, she wants to stop working for five years and spend her savings traveling, hiking ,partying, buying her self expensive clothes etc.

I asked her if she has enough savings to cover her half of the bills and she said she doesn’t intend to cover any bills, and will use all her savings on herself, so she is basically asking me to cover all our bills and our son's expenses while she spends her money on entertainment. I told that if she did that I will be left with almost zero savings every month basically living from check to check, she said she sees no problem in that and I can work overtime if I had to.

I was shocked by her answer, It made me question If she even cares about me, she basically has no problem making me struggle while she uses her money for entertainment so I told her that whether she stops working or not is her decision but i will not cover her half of the bills, I won't burn my self covering the expenses of someone with a high paying job while she entertains her self because I believe that is extremely unfair towards me, I reminded her that I have been covering all our son's expenses and half of bills despite the pay gap so I have already been saving less and now she wants me to drain my saving and burn my self out so that she can entertain herself, absolutely not.

Now she is angry and ranting about how I don't appreciate her and the hard work she has been doing all her life.

So , AITA
"""

texto2 = """
AITJ for blocking an old friend after she said how h*rny she was to my bf
Bit of a long one. This situation includes me (21)(F) and my bf (20)(M) and a girl who i will call K (21) for the sake of anonymity.

K and i were friends throughout school but we constantly fell out, she was always seeking for attention in our friend group and would smack my ass and kiss me in front of them which would make me uncomfortable. After that in college i kept my distance with K and we didn't speak much, but then i met BF. I was aware that he was aquaintences with K but they didn't speak much so i didn't really care.

Me and BF have been together for for 2 years now and we would see her around often, we always chatted to her but it was obviously tense between us and i didn't want to make friends again. Recently BF came home from the shops mortified, telling me that K had come up to him saying she was going off her birth control and that she was so h*rny that she could fuck any guy she saw.

It made BF uncomfortable and made me seethe in rage so i sent her a long paragraph about how her oversexualised comments are inappropriate and gross and she knows what she's doing but she laughed it off so i told her to leave us alone and blocked her and BF did the same. Now she keeps trying to speak to us and my best mate (T) and refuses to leave us alone.

TLDR; cut off old school friend for doing horny talk at my bf of 2 years

EDIT: cheers guys, honestly after typing it all out i've thought back to a lot of other things K has done in the past.. far too long for a post on here but i've come to the conclusion that i did the right thing, me and BF have decided we will both just disappear off if we see her, lol :)
"""

async def corregir_texto(texto):
    prompt = f"""
    - I will give you a text about a person asking if they are the jerks for doing something.
    - I want you to use the text to rewrite the story with good grammar and make it more comprehensive and short, make it last about 1 minute.
    - If the story says anything about the age and geneder of the characters, keep them. For example, I(20M) or my wife (20F).
    - Return only the text and nothing else.
    - Do not add any comments or explanations about what you did, I only need the corrected text.
    - Do not tell me "Here's a rewritten version of the text with improved grammar and clarity" or nothing like that, seriously, I only need the story, any coments may ruin it.

    Text: {texto}
    """
     
    response = await AsyncClient().generate('llama3.2', prompt)
    texto_corregido = response['response']
    
    #print(texto_corregido)

    return texto_corregido


async def crear_titulo(texto):
    prompt = f"""
    - I will give you a text about a person asking if they are the jerks for doing something.
    - I want you to create a question about the text, like, I am the jerk for x.
    - Dont use abreviations.
    - Do not add any comments or explanations about what you did, I only need the corrected text.
    - Do not tell me "Here's a rewritten version of the text with improved grammar and clarity" or anything like that, seriously, I only need the story, any coments may ruin it.

    Text: {texto}
    """
     
    response = await AsyncClient().generate('llama3.2', prompt)
    titulo = response['response']
    
    #print(titulo)

    return titulo

print(asyncio.run(crear_titulo(texto2)))
