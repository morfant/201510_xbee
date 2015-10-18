o = OSCFunc({|msg, time, addr, recvPort| msg.postln}, '/xbee');
o.free;



(
SynthDef.new(\di,
	{
		arg freq = 50, mf = 10, cf = 10, panfreq = 1/10, amp = 0.4;
		var mod = SinOsc.kr(mf);
		var fm = SinOsc.kr(cf);
//		var sig = LFNoise0.ar(freq, mul: mod);
		var sig = SinOsc.ar(freq * fm, mul: mod);
		var pan = SinOsc.kr(panfreq);
		Out.ar(0, Pan2.ar(sig, pan, amp));
	}
).add;
)


(
SynthDef.new(\ti,
	{
		arg freq = 50, mf = 10, cf = 10, panfreq = 1/10, amp = 0.4;
		var mod = SinOsc.kr(mf);
		var fm = SinOsc.kr(cf);
//		var sig = LFNoise0.ar(freq, mul: mod);
		var sig = Impulse.ar(freq);
		var pan = SinOsc.kr(panfreq);
		Out.ar(0, Pan2.ar(sig, 0, amp));
	}
).add;
)

1.asDigit
1.asAscii
'1'.asDigits

2007.asDigits(10);

(
a = Synth(\di);b = Synth(\ti);

p = OSCFunc({|msg, time, addr, recvPort|
	var v = msg[1].asInteger.abs;
//	var m = msg[2].asInteger.abs;
//	msg[1].class.postln;
	("v: " + v).postln;
//	("m: " + m).postln;

	if (v < 60, {
		b.set(\amp, 0);
		a.set(\amp, 1);
		a.set(\freq, 1 + ((v)*10));
		},
		{
		a.set(\amp, 0);
		b.set(\amp, 1);
		b.set(\freq, 1 + ((v)/10));
	});
}, '/dist_AB');
)
