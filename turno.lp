% PREPROCESSING -----------------------------------------------------------------------

#const day_shift=2.
#const night_shift=2.

#defined max_hours/1.
#defined hours/3.
#defined day_to_weekday/2.
% day_to_weekday(day number, type of weekday as a number)

#defined day_to_week/2.
% day_to_week(day number, week number)

#defined max_days/1.

special_days(P) :- special_days(P,_).

week(0..4, weekday).
week(5,sat).
week(6,sun).
%#show week/2.

persons(C) :- C = #count{ P : person(P) }.

day(1..D) :- max_days(D).

turn_days(P,Min,Max) :- person(P), not special_days(P), min_max(Min,Max).
turn_days(P,M,M) :- special_days(P,M).

fixed_days(S) :- #sum{D,P: special_days(P,D) } = S.
fixed_persons(F) :- #count{P: special_days(P) } = F.


min_max(@min_max((D,S,P,F)), @min_max((D,S,P,F))+1) :- persons(P), fixed_days(S), fixed_persons(F), max_days(D).

%#show min_max/2.

% SHIFT ASSIGNMENT -----------------------------------------------------------------------

% for each day, assign 2 persons for the day shift and 2 for the night shift
2 {assigned(day,P,D) : person(P)} 2 :- day(D).
2 {assigned(night,P,D) : person(P)} 2 :- day(D).

% try to evenly distribute shifts to half as day and half as night shifts
Min/2 {assigned(day,P,D) : day(D)} Max/2 + 1 :- person(P), turn_days(P,Min,Max), not exception(even_distribution, (P)).
Min/2 {assigned(night,P,D) : day(D)} Max/2 + 1:- person(P), turn_days(P,Min,Max), not exception(even_distribution, (P)).

:- {assigned(_,P,D) : day(D)} Min-1, person(P), turn_days(P,Min,Max).
:- Max+1 {assigned(_,P,D) : day(D)}, person(P), turn_days(P,Min,Max).

% no 2 nights in a row
:- assigned(night,P,D), assigned(night,P,D+1), day(D), day(D+1).

% no night shift followed by day shift
:- assigned(night,P,D), assigned(day,P,D+1), day(D), day(D+1).

% no day shift followed by night shift
:- assigned(day,P,D), assigned(night,P,D), day(D).


% condiciones especiales

% must have certain amount of shifts in the given weekday type (and shift type)
% P person | N weekday sat sun | T day night | C amount of times
:- constraint(type_count, (P,N,T,C)), {assigned(T,P,D) : day_to_weekday(D,W), week(W,N)} != C.
% if no T is present then we assume it can be either day or night
:- constraint(type_count, (P,N,C)), {assigned(_,P,D) : day_to_weekday(D,W), week(W,N)} != C.

% can have at most 1 shift in a given week for the given weekday type
% P person | N weekday sat sun
:- constraint(at_most_once_a_week, (P,N)), assigned(_,P,D), assigned(_,P,D'),
    day_to_weekday(D,M), day_to_weekday(D',M'),
    week(M,N), week(M',N),
    day_to_week(D,W), day_to_week(D',W), D < D'.

% can not have 2 singles in the same shift
:- assigned(T,P,D), assigned(T,P',D), P<P', single(P), single(P').

% must not assign a person to a blocked day
:- constraint(blocked, (P,D)), assigned(_,P,D).
:- constraint(fixed, (P,T,D)), not assigned(T,P,D).

%#show assigned/3.

% OPTIMIZATION --------------------------------------------------------------------------

% try to evenly distribute extra hours for each person

hours_per_person(M/P) :- max_hours(M), persons(P).

hours_per_person(P,T) :- T = #sum{ H,S,D : assigned(S,P,D), hours(S,D,H)}, person(P).

max_total_hours(T) :- hours_per_person(P,T).
max_total_hours(T-1) :- max_total_hours(T), T > 0.

#minimize{T: max_total_hours(T)}.

%#show hours_per_person/1.
%#show max_hours/1.
%#show hours_per_person/2.
#show.