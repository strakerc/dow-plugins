# Shared contact-data detection for the dow-plugins hooks.
# ---------------------------------------------------------------------------
# Sourced by .githooks/pre-commit (staged file content) and .githooks/commit-msg
# (the message itself). One copy on purpose: a leak-prevention pattern kept in
# two places is one edit away from protecting only half of what it claims to.
#
# Not executable and has no shebang -- it is sourced, never run.
#
# Exemptions are by VALUE, never by file or by context:
#   phones  - the reserved fictional range, any area code + 555 + 01XX
#   emails  - example.com, example.org, example.net
# Callers may filter further; commit-msg additionally exempts noreply identities.

# Boundaries must NOT be consumed. Under the ERE fallback a match eats the
# character separating it from the next number, so a single -o pass sees only the
# first of two adjacent numbers -- and if that one is an exempt placeholder, the
# real number beside it is never examined. PCRE lookarounds do not consume.
# Probe rather than assume: macOS ships BSD grep, which has no -P at all.
# The probe string is deliberately not phone-shaped; earlier drafts used real
# formats here and the hook blocked its own source.
if echo 'x12 34' | grep -qoP '(?<![0-9])12' 2>/dev/null; then
  PHONE_GREP="-oP"
  PHONE_RE='(?<![0-9])\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}(?![0-9])'
  PHONE_FILTER="-P"
else
  PHONE_GREP="-oE"
  PHONE_RE='(^|[^0-9])\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}([^0-9]|$)'
  PHONE_FILTER="-E"
fi
EMAIL_RE='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

bad_phone_in() { # echoes the digits of any non-exempt number on the line
  # One match at a time, re-supplying a non-digit boundary each round, so the
  # ERE fallback behaves identically to the PCRE path rather than being the
  # untested half. Harmless under PCRE, where nothing is consumed.
  _rest=$1
  while :; do
    _m=$(printf '%s' "$_rest" | grep $PHONE_GREP "$PHONE_RE" | head -1)
    [ -z "$_m" ] && break
    printf '%s' "$_m" | sed 's/[^0-9]//g' \
      | grep -E '^[0-9]{10}$' | grep -vE '^[0-9]{3}55501[0-9]{2}$'
    _next=${_rest#*"$_m"}
    [ "$_next" = "$_rest" ] && break   # no progress; refuse to spin
    _rest="x$_next"
  done
}

bad_email_in() {
  printf '%s' "$1" | grep -oE "$EMAIL_RE" \
    | grep -viE '@example\.(com|org|net)$'
}
