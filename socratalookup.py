from soclient import SoClient

class SocrataLookup:

	@classmethod
	def get_signs(cls, lat, lon, meters):
		cl = SoClient("data.seattle.gov", "it8u-sznv")
		
		meters_per_degree = 111185.10693302986
		degrees = meters / meters_per_degree

		lat_min = lat - degrees
		lat_max = lat + degrees

		lon_min = lon - degrees
		lon_max = lon + degrees

		return cl.query(
			cl.AND(
				cl.GREATER_THAN(cl.COL("latitude"), cl.VAL(lat_min)),
				cl.LESS_THAN(cl.COL("latitude"), cl.VAL(lat_max)),
				cl.GREATER_THAN(cl.COL("longitude"), cl.VAL(lon_min)),
				cl.LESS_THAN(cl.COL("longitude"), cl.VAL(lon_max))
			)
		)

	@classmethod
	def get_crimes(cls, lat, lon, meters):
		cl = SoClient("data.seattle.gov", "7ais-f98f")

		return cl.query(
			cl.AND(
				cl.OR(
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-CARPROWL")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-OTH")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-AUTO")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-RES")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-NONAGG")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("WARRARR-FELONY")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("DISTURBANCE-OTH")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-NOFORCE-RES")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-FORCE-NONRES")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-AUTOACC")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("HARASSMENT")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-BICYCLE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-BODYFORCE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-WEAPON")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-NOFORCE-NONRES")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-LICENSE PLATE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-RCVD-FOR OTHER AGENCY")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-SECURE PARKING-RES")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("NARC-SELL-COCAINE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-BODYFORCE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("DUI-LIQUOR")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-TRUCK")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("PROSTITUTION")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-PKPOCKET")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-POSSESSION")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-MTRCYCLE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-WEAPON")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-STREET-GUN")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THEFT-AUTO PARTS")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("PROPERTY STOLEN-POSSESS")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-NONAGG-POLICE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ASSLT-AGG-GUN")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-RCVD-FOR OTHAGY")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("BURGLARY-SECURE PARKING-NONRES")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-UNLAWFUL USE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("THREATS-WEAPON")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-BUSINESS-GUN")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-BUSINESS-WEAPON")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("INJURY - OTHER")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("INJURY - ACCIDENTAL")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("NARC-SELL-HEROIN")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-RESIDENCE-BODYFORCE")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("ROBBERY-RESIDENCE-GUN")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("VEH-THEFT-TRAILER")),
					cl.EQUALS(cl.COL("offense_type"), cl.VAL("WEAPON-CONCEALED"))
				),
				cl.CIRCLE("location", lat, lon, meters),
				cl.GREATER_THAN(cl.COL("occurred_date_or_date_range_start"), cl.VAL("1900-01-01T00:00:00"))
			)
		)