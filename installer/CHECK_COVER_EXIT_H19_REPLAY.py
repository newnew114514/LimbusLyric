from pathlib import Path
import ast, sys, types

ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)>1:
    main=Path(sys.argv[1])
else:
    matches=list(ROOT.glob('LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'))
    main=matches[0]
source=main.read_text(encoding='utf-8')
assert 'COVER FOLLOW + MIRRORED EXIT H19' in source
assert source.index('# H19 cover-follow + mirrored exit closure') < source.index('# H14 auto-precision deadline / bounded enhancement')
for token in [
    '_h16_cover_pic_url = _h19_cover_pic_url',
    '_h16_cover_color_from_image = _h19_cover_color_from_image',
    'FadingLine.update=_h19_fading_update',
    'FadingLine.draw=_h19_fading_draw',
    "('跟随进场反向（推荐）','mirror')",
    'H16_COVER_RETRY_SEC = (2.0, 6.0, 18.0, 30.0, 60.0, 120.0)',
]:
    assert token in source, token

tree=ast.parse(source)
want={
    '_h19_https_url','_h19_cover_artist_ok','_h19_cover_pic_url','_h19_smoothstep',
    '_h19_exit_motion','_h19_exit_alpha'
}
nodes=[]
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in want:
        nodes.append(node)
assert {n.name for n in nodes}==want
mod=ast.Module(body=nodes,type_ignores=[]); ast.fix_missing_locations(mod)

calls=[]
class Resp:
    def raise_for_status(self): pass
    def json(self):
        return {'songs':[{'album':{'picUrl':'http://p1.music.126.net/test.jpg'}}]}
class Requests:
    @staticmethod
    def get(url, **kwargs):
        calls.append((url,kwargs))
        return Resp()

def alias_match(a,b):
    return (False, '')

ns={
    're':__import__('re'),'math':__import__('math'),'requests':Requests,
    '_LIMBUS_H19_COVER_PIC_PRE':lambda row:'',
    '_LIMBUS_H19_COVER_ARTIST_PRE':lambda wanted,row_artists:False,
    '_artist_alias_match':alias_match,
    'write_error_log':lambda *a,**k:None,
}
exec(compile(mod,str(main),'exec'),ns)
assert ns['_h19_https_url']('http://a/b')=='https://a/b'
assert ns['_h19_https_url']('file:///x')==''
url=ns['_h19_cover_pic_url']({'id':33516239,'album':{'id':123,'picId':456}})
assert url=='https://p1.music.126.net/test.jpg',url
assert calls and calls[0][0]=='https://music.163.com/api/song/detail/'
assert calls[0][1].get('timeout')==4
# Multi-artist UI identity may contain a featured vocalist omitted by the provider row.
assert ns['_h19_cover_artist_ok']('椎名もた, 鏡音リン',[{'name':'椎名もた'}]) is True

motion=ns['_h19_exit_motion']
assert abs(motion('reverse_rise',0.0)[1])<1e-9
assert 12.9 < motion('reverse_rise',1.0)[1] < 13.1
assert abs(motion('reverse_slide',0.0)[0])<1e-9
assert -15.1 < motion('reverse_slide',1.0)[0] < -14.9
assert abs(motion('reverse_bounce',0.0)[1])<1e-9
assert 10.9 < motion('reverse_bounce',1.0)[1] < 11.1
alpha=ns['_h19_exit_alpha']
assert alpha('reverse_soft',0.0)==255 and alpha('reverse_soft',1.0)==0
assert alpha('reverse_typewriter',0.0)==255 and alpha('reverse_typewriter',1.0)==255
print('COVER + MIRRORED EXIT H19 REPLAY: PASS')
